from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required

@login_required
def logout(request):
    auth_logout(request)
    return redirect('accounts.login')

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    
    if request.method == 'GET':
        # If user is already logged in, redirect them to appropriate dashboard
        if request.user.is_authenticated:
            if request.user.role == 'HCP':
                return redirect('professional_dashboard')
            else:
                return redirect('patient_dashboard')
        return render(request, 'accounts/log-in.html', {'template_data': template_data})
    
    elif request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['Username'],
            password=request.POST['Password']
        )
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/log-in.html', {'template_data': template_data})
        
        auth_login(request, user)
        if user.role == 'HCP':
            return redirect('professional_dashboard')
        elif user.role == 'admin':
            return redirect('admin_management')
        
        return redirect('patient_dashboard')

