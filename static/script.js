// Toggle password visibility
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Toggle modal visibility
function toggleModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.toggle('show');
    
    if (modal.classList.contains('show')) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = 'auto';
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
}

// Confirm delete action
function confirmDelete(itemType) {
    return confirm(`Are you sure you want to delete this ${itemType}? This action cannot be undone.`);
}

// Edit Skill
function editSkill(id, name, category, proficiency) {
    document.getElementById('edit_skill_id').value = id;
    document.getElementById('edit_skill_name').value = name;
    document.getElementById('edit_category').value = category;
    document.getElementById('edit_proficiency').value = proficiency;
    
    const form = document.getElementById('editSkillForm');
    form.action = `/edit_skill/${id}`;
    
    toggleModal('editSkillModal');
}

// Edit Project
function editProject(id, name, description, technologies, github_link) {
    document.getElementById('edit_project_id').value = id;
    document.getElementById('edit_project_name').value = name;
    document.getElementById('edit_project_description').value = description;
    document.getElementById('edit_technologies').value = technologies;
    document.getElementById('edit_github_link').value = github_link;
    
    const form = document.getElementById('editProjectForm');
    form.action = `/edit_project/${id}`;
    
    toggleModal('editProjectModal');
}

// Edit Certification
function editCertification(id, name, organization, date_earned) {
    document.getElementById('edit_cert_id').value = id;
    document.getElementById('edit_certification_name').value = name;
    document.getElementById('edit_organization').value = organization;
    document.getElementById('edit_date_earned').value = date_earned;
    
    const form = document.getElementById('editCertificationForm');
    form.action = `/edit_certification/${id}`;
    
    toggleModal('editCertificationModal');
}

// Edit Internship
function editInternship(id, company, role, duration, description) {
    document.getElementById('edit_internship_id').value = id;
    document.getElementById('edit_company').value = company;
    document.getElementById('edit_role').value = role;
    document.getElementById('edit_duration').value = duration;
    document.getElementById('edit_internship_description').value = description;
    
    const form = document.getElementById('editInternshipForm');
    form.action = `/edit_internship/${id}`;
    
    toggleModal('editInternshipModal');
}

// Print resume
function printResume() {
    window.print();
}

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    // Password match validation
    const registerForm = document.querySelector('.auth-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');
            
            if (password && confirmPassword && password.value !== confirmPassword.value) {
                e.preventDefault();
                alert('Passwords do not match!');
                return false;
            }
        });
    }
    
    // Add smooth scroll to sections
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Add animation to cards on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.card, .stat-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease';
        observer.observe(card);
    });
});

// Auto-hide alerts after 5 seconds
setTimeout(function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.style.transition = 'opacity 0.5s ease';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 500);
    });
}, 5000);