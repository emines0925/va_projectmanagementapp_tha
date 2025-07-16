from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View

from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import status, permissions
from .models import Comment, Project
from .serializers import CommentSerializer
from .forms import UserSignUpForm, AddUserToProjectForm, ProjectForm, UserLoginForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Project, ProjectMembership  
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Comment, ProjectMembership

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
        project_pk = kwargs.get('pk') or kwargs.get('project_pk')
        if not project_pk:
            raise ValueError("View using UserRoleRequiredMixin is missing 'pk' or 'project_pk' in its URL pattern.")
            
        try:
            membership = ProjectMembership.objects.get(
                project__pk=project_pk, 
                user=request.user
            )
        except ProjectMembership.DoesNotExist:
            raise Http404

        if membership.role not in self.required_roles:
            raise PermissionDenied

        # If all checks pass, proceed to the actual view (e.g., the delete method)
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
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        try:
            membership = ProjectMembership.objects.get(
                project=project,
                user=self.request.user
            )
            context['user_role'] = membership.role
        except ProjectMembership.DoesNotExist:
            context['user_role'] = None
            
        return context
    
class ProjectCreateView(LoginRequiredMixin, CreateView):
    """
    Displays a form to create a new project.
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:project-list') 
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        if request.htmx:
            form = self.get_form()
            return render(request, 'projects/_project_form_partial.html', {'form': form})
        
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        """
        This method is called when valid form data has been POSTed.
        """
        self.object = form.save()
        ProjectMembership.objects.create(
            project=self.object,
            user=self.request.user,
            role='Owner'
        )
        
        if self.request.htmx:
            projects = Project.objects.filter(members=self.request.user).order_by('-updated_at')
            return render(self.request, 'projects/_project_list_partial.html', {'projects': projects})

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('project-list')

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
        context = {'project': project, 'members': members, 'form': form}
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
                ProjectMembership.objects.create(project=project, user=user_to_add, role=role)

            if request.htmx:
                members = ProjectMembership.objects.filter(project=project).order_by('user__username')
                return render(request, 'projects/_member_list_partial.html', {'project': project, 'members': members})
            
            return redirect('projects:project-manage-users', pk=project.pk)
        
        members = ProjectMembership.objects.filter(project=project).order_by('user__username')
        context = {'project': project, 'members': members, 'form': form}
        return render(request, self.template_name, context)


class RemoveUserFromProjectView(LoginRequiredMixin, UserRoleRequiredMixin, View):
    required_roles = ['Owner']

    def dispatch(self, request, *args, **kwargs):
        project_pk = kwargs.get('project_pk')
        membership = get_object_or_404(ProjectMembership, project__pk=project_pk, user=request.user)
        if membership.role not in self.required_roles:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, project_pk, user_pk):
        project = get_object_or_404(Project, pk=project_pk)
        user_to_remove = get_object_or_404(User, pk=user_pk)
        
        membership = get_object_or_404(
            ProjectMembership, project=project, user=user_to_remove
        )
        
        if membership.role == 'Owner':
            return HttpResponse("Cannot remove the project owner.", status=400)

        membership.delete()
        
        return HttpResponse(status=200)
    
class CommentOnProject(UserRoleRequiredMixin, LoginRequiredMixin, View):
    """
    Allows users to comment on a project.
    """

    required_roles = ['Owner', 'Editor']
    def post(self, request, pk):
        project = Project.objects.get(pk=pk)
        if request.content_type == 'application/json':
            import json
            try:
                data = json.loads(request.body)
            except Exception:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
        else:
            data = request.POST
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            comment = Comment.objects.create(
                project=project,
                user=request.user,
                text=serializer.validated_data['text']
            )
            comment.save()
            return HttpResponse(project.comments, status=status.HTTP_201_CREATED)
        return HttpResponse(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
    

class DeleteComment(UserRoleRequiredMixin, LoginRequiredMixin, View):
    """
    Allows users to delete their own comments or the project owner's comments.
    """
    required_roles = ['Owner']

    def post(self, request, project_pk, comment_pk):
        project = get_object_or_404(Project, pk=project_pk)
        comment = get_object_or_404(Comment, pk=comment_pk, project=project)

        comment.delete()

        if request.htmx:
            return HttpResponse(status=204)  # No content response for HTMX

        return redirect('projects:project-detail', pk=project.pk)