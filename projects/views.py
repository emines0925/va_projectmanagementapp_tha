from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from .forms import UserSignUpForm, AddUserToProjectForm, ProjectForm, UserLoginForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Project, ProjectMembership  
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, Http404
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.models import User

class UserRoleRequiredMixin:
    """
    A mixin that verifies a user has one of the specified roles for a project.
    
    How it works:
    1. It looks for a `required_roles` list in the View it's attached to.
    2. It gets the project's primary key (pk) from the URL.
    3. It tries to find a ProjectMembership for the current user and project.
       - If none is found -> Raise Http404 (user isn't a member).
    4. If membership is found, it checks if the user's role is in `required_roles`.
       - If the role is not allowed -> Raise PermissionDenied (403 Forbidden).
    5. If all checks pass, the view proceeds as normal.
    """
    required_roles = []

    def dispatch(self, request, *args, **kwargs):
        project_pk = self.kwargs.get('pk')
        if not project_pk:
            raise ValueError("View is missing project 'pk' in URL.")
        membership = get_object_or_404(
            ProjectMembership, 
            project__pk=project_pk, 
            user=request.user
        )

        if membership.role not in self.required_roles:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

def signup_view(request):
    """
    Handles user registration.
    - On GET request, it displays an empty registration form.
    - On POST request, it validates the submitted data. If valid, it creates
      a new user, logs them in, and redirects to the main project list.
    - Function-based view is preferred to define a custom action of directly logging in the user after registration.   
    """
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('projects:project-list')
    else:
        form = UserSignUpForm()
    
    return render(request, 'projects/signup.html', {'form': form})

# --- Login View (Class-Based) ---
class UserLoginView(LoginView):
    """
    Handles user login using Django's built-in LoginView for security and simplicity.
    - `template_name`: Specifies the template to use for the login form.
    - `form_class`: Uses our custom form to add CSS classes and placeholders.
    - `redirect_authenticated_user`: If a user is already logged in, they will be
      redirected from the login page to the success URL.
    - `success_url`: The URL to redirect to upon successful login. `reverse_lazy`
      ensures the URL is not resolved until it's needed.
    """
    template_name = 'projects/login.html'
    form_class = UserLoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('projects:project-list')


# --- Logout View (Class-Based) ---
class UserLogoutView(LogoutView):
    """
    Handles user logout using Django's built-in LogoutView.
    - `next_page`: The URL to redirect to after the user has been logged out.
      The login page is a sensible default.
    """
    next_page = reverse_lazy('login')

class ProjectListView(LoginRequiredMixin, ListView):
    """
    Displays a list of projects.
    - Uses Django's ListView to automatically handle the retrieval and display of project objects.
    - The template will be 'projects/project_list.html'.
    """
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        """
        Returns a queryset of projects where the currently logged-in user
        is a member.
        """
        return Project.objects.filter(members=self.request.user).order_by('-updated_at')

class ProjectDetailView(LoginRequiredMixin, DetailView):
    """
    Displays the details of a single project.
    """
    model = Project
    template_name = 'projects/project_detail.html'

    def get_queryset(self):
        return Project.objects.filter(members=self.request.user)

    def get_context_data(self, **kwargs):
        # 1. First, call the base implementation to get the default context
        context = super().get_context_data(**kwargs)
        
        # 2. Get the project object from the context
        project = self.get_object()
        
        # 3. Find the membership for the current user and this specific project.
        #    We wrap it in a try-except block in case something unexpected happens.
        try:
            membership = ProjectMembership.objects.get(
                project=project,
                user=self.request.user
            )
            # 4. Add the user's role to the context
            context['user_role'] = membership.role
        except ProjectMembership.DoesNotExist:
            # This should ideally not happen if get_queryset is working correctly,
            # but it's a safe fallback.
            context['user_role'] = None
            
        # 5. Return the updated context
        return context
    
class ProjectCreateView(LoginRequiredMixin, CreateView):
    """
    Displays a form to create a new project.
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:project-list') 

    def form_valid(self, form):
        """
        This method is called when valid form data has been POSTed.
        It should return an HttpResponse.
        """
        response = super().form_valid(form)
        
        ProjectMembership.objects.create(
            project=self.object,
            user=self.request.user,
            role='Owner'
        )
        
        return response

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    """
    Displays a form to edit an existing project.
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    required_roles = ['Owner', 'Editor']
    
    def get_success_url(self):
        """Redirect to the detail view of the project that was just updated."""
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.pk})

    def get_success_url(self):
        """Redirect to the detail view of the project that was just updated."""
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(UserRoleRequiredMixin, LoginRequiredMixin, DeleteView):
    """
    Presents a confirmation page before deleting a project.
    """
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:project-list')
    required_roles = ['Owner']

class ManageProjectUsersView(LoginRequiredMixin, UserRoleRequiredMixin, View):
    """
    A view for the project 'Owner' to manage users in their project.
    - Displays a list of current members.
    - Provides a form to add new members.
    """
    template_name = 'projects/manage_users.html'
    required_roles = ['Owner']
    def get(self, request, pk):
        """Handles GET requests: Displays the page with user list and add form."""
        project = get_object_or_404(Project, pk=pk)
        members = ProjectMembership.objects.filter(project=project).order_by('user__username')
        form = AddUserToProjectForm()

        context = {
            'project': project,
            'members': members,
            'form': form
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        """Handles POST requests: Processes the form to add a new user."""
        project = get_object_or_404(Project, pk=pk)
        form = AddUserToProjectForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            role = form.cleaned_data['role']
            user_to_add = User.objects.get(username=username)

            if ProjectMembership.objects.filter(project=project, user=user_to_add).exists():
                messages.error(request, f"User '{username}' is already a member of this project.")
            else:
                ProjectMembership.objects.create(
                    project=project,
                    user=user_to_add,
                    role=role
                )
                messages.success(request, f"Successfully added '{username}' as an {role}.")
            
            return redirect('projects:project-manage-users', pk=project.pk)
        
        members = ProjectMembership.objects.filter(project=project).order_by('user__username')
        context = {
            'project': project,
            'members': members,
            'form': form
        }
        return render(request, self.template_name, context)