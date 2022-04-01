
$(document).ready(function() {
    // the first time page loaded
    const loadingMessageJson = $('#first-loading-message').attr("data-message");
    if ( loadingMessageJson !== '' )
    {
        const loadingMessageObj = JSON.parse(loadingMessageJson);
        if ( loadingMessageObj.hasOwnProperty("danger") )
        {
            $("#danger-alert").show();
            $("#danger-alert").html(loadingMessageObj.danger);
            $("#danger-alert").fadeTo(4000, 500).slideUp(500, function(){
                $("#danger-alert").slideUp(6000);
                $("#danger-alert").html('');
                $("#danger-alert").hide();
            });
        }
        else if ( loadingMessageObj.hasOwnProperty("success") )
        {
            $("#success-alert").show();
            $("#success-alert").html(loadingMessageObj.success);
            $("#success-alert").fadeTo(4000, 500).slideUp(500, function(){
                $("#success-alert").slideUp(6000);
                $("#success-alert").html('');
                $("#success-alert").hide();
            });
        }
    }

    // clean the hidden input value
    $('#first-loading-message').attr("data-message", "");
});

function post_signup(e){
    e.preventDefault();
    const form = $('#signup-form')[0];
    const email = form.elements.signup_email.value;
    const password = form.elements.signup_password.value;
    const password_check = form.elements.signup_password_check.value;
    const postUrl = $('#post-user-url').attr("data-url");

    $('#signup_email').removeClass("border-danger");
    $('#signup_password').removeClass("border-danger");
    $('#signup_password_check').removeClass("border-danger");
    $("#signup-danger-alert").html('');
    $("#signup-danger-alert").hide();

    $('#signup_button').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Loading...')
                       .attr('disabled', true);

    $.ajax({
        type:'POST',
        url:postUrl,
        data:{
            email:email,
            password:password,
            password_check:password_check,
        },
        success:function(data){
            $('#signup_button').html('Sign up')
                               .attr('disabled', false);

            if ( data.success === true )
            {
                $('#signupModal').modal('hide');
                $(':input','#signup-form')
                    .not(':button, :submit, :reset, :hidden')
                    .val('');
                $("#success-alert").show();
                $("#success-alert").html('Create successful. Please take a look in you email box.');
                $("#success-alert").fadeTo(4000, 500).slideUp(500, function(){
                    $("#success-alert").slideUp(6000);
                    $("#success-alert").html('');
                    $("#success-alert").hide();
                });
            }
            else
            {
                var message = "";
                var is_password_error = false;
                var is_email_error = false;
                for (const [key, values] of Object.entries(data.errors))
                {
                    if ( key === 'password' || key === '__all__' )
                    {
                        is_password_error = true;
                    }
                    else
                    {
                        is_email_error = true;
                        is_password_error = true;
                    }

                    values.forEach(function(item, index, array) {
                        message += item + "<br>";
                    });
                }

                $("#signup-danger-alert").html(message);
                $("#signup-danger-alert").show();
                if ( is_email_error )
                {
                    $('#signup_email').addClass("border-danger");
                }
                if ( is_password_error )
                {
                    $('#signup_password').addClass("border-danger");
                    $('#signup_password_check').addClass("border-danger");
                }
            }
        },
        error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}

function post_login(e){
    e.preventDefault();
    const form = $('#login-form')[0];
    const email = form.elements.login_email.value;
    const password = form.elements.login_password.value;
    const crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
    const postUrl = $('#post-login').attr("data-url");

    $('#login_email').removeClass("border-danger");
    $('#login_password').removeClass("border-danger");
    $("#login-danger-alert").html('');
    $("#login-danger-alert").hide();

    $('#login_button').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Loading...')
                      .attr('disabled', true);

    $.ajax({
        type:'POST',
        url:postUrl,
        data:{
            email:email,
            password:password,
        },
        headers:{"X-CSRFToken": crf_token},
        success:function(data){
            $('#login_button').html('Login')
                              .attr('disabled', false);

            if ( data.success === true )
            {
                $('#loginModal').modal('hide');
                $(':input','#login-form')
                    .not(':button, :submit, :reset, :hidden')
                    .val('');
                var message = "Login successful! Reloading...";
                $("#success-alert").show();
                $("#success-alert").html(
                    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' + message
                );
                $("#success-alert").fadeTo(4000, 500).slideUp(500, function(){
                    $("#success-alert").slideUp(6000, function(){
                        const currentUrl = $('#current-page').attr("data-url");
                        window.location.href = currentUrl;
                    });
                    $("#success-alert").html('');
                    $("#success-alert").hide();
                });
            }
            else
            {
                var message = "";
                for (const [key, values] of Object.entries(data.errors))
                {
                    values.forEach(function(item, index, array) {
                        message += item + "<br>";
                    });
                }

                $("#login-danger-alert").html(message);
                $("#login-danger-alert").show();
                $('#login_email').addClass("border-danger");
                $('#login_password').addClass("border-danger");
            }
        },
        error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}

function patch_username(e){
    e.preventDefault();

    const form = $('#username-form')[0];
    const username = form.elements.newusername.value;
    const crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
    const patchUrl = $('#pk-url').attr("data-url");

    $('#newusername').removeClass("border-danger");
    $("#username-danger-alert").html('');
    $("#username-danger-alert").hide();

    $('#username-button').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Loading...')
                         .attr('disabled', true);

    $.ajax({
        type:'PATCH',
        url:patchUrl,
        data:{
            action: 'username',
            username: username,
        },
        headers:{"X-CSRFToken": crf_token},
        success:function(data){
            $('#username-button').html('Update')
                                 .attr('disabled', false);

            if ( data.success === true )
            {
                $(':input','#username-form')
                    .not(':button, :submit, :reset, :hidden')
                    .val('');
                var message = "Username updated successful! Reloading...";
                $("#username-success-alert").show();
                $("#username-success-alert").html(
                    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' + message
                );
                $("#username-success-alert").fadeTo(4000, 500).slideUp(500, function(){
                    $("#username-success-alert").slideUp(6000, function(){
                        const currentUrl = $('#current-page').attr("data-url");
                        window.location.href = currentUrl;
                    });
                    $("#username-success-alert").html('');
                    $("#username-success-alert").hide();
                });
            }
            else
            {
                var message = "";
                for (const [key, values] of Object.entries(data.errors))
                {
                    values.forEach(function(item, index, array) {
                        message += item + "<br>";
                    });
                }

                $("#username-danger-alert").html(message);
                $("#username-danger-alert").show();
                $('#newusername').addClass("border-danger");
            }
        },
        error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}

function patch_password(e){
    e.preventDefault();

    const form = $('#password-form')[0];
    const password = form.elements.oldPassword.value;
    const new_password = form.elements.newPassword.value;
    const new_password_check = form.elements.newPasswordCheck.value;
    const crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
    const patchUrl = $('#pk-url').attr("data-url");

    $('#oldPassword').removeClass("border-danger");
    $('#newPassword').removeClass("border-danger");
    $('#newPasswordCheck').removeClass("border-danger");
    $("#password-danger-alert").html('');
    $("#password-danger-alert").hide();

    $('#password-button').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Loading...')
                         .attr('disabled', true);

    $.ajax({
        type:'PATCH',
        url:patchUrl,
        data:{
            action: 'password',
            password: password,
            new_password: new_password,
            new_password_check: new_password_check,
        },
        headers:{"X-CSRFToken": crf_token},
        success:function(data){
            $('#password-button').html('Update')
                                 .attr('disabled', false);

            if ( data.success === true )
            {
                $(':input','#password-form')
                    .not(':button, :submit, :reset, :hidden')
                    .val('');
                var message = "Password updated successful! Reloading...";
                $("#password-success-alert").show();
                $("#password-success-alert").html(
                    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' + message
                );
                $("#password-success-alert").fadeTo(4000, 500).slideUp(500, function(){
                    $("#password-success-alert").slideUp(6000, function(){
                        const currentUrl = $('#current-page').attr("data-url");
                        window.location.href = currentUrl;
                    });
                    $("#password-success-alert").html('');
                    $("#password-success-alert").hide();
                });
            }
            else
            {
                var message = "";
                for (const [key, values] of Object.entries(data.errors))
                {
                    values.forEach(function(item, index, array) {
                        message += item + "<br>";
                    });
                }

                $("#password-danger-alert").html(message);
                $("#password-danger-alert").show();
                $('#oldPassword').addClass("border-danger");
                $('#newPassword').addClass("border-danger");
                $('#newPasswordCheck').addClass("border-danger");
            }
        },
        error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}

function resend_activate_email(e){
    e.preventDefault();

    const crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');
    const targetUrl = $('#resend-activate-email-url').attr("data-url");

    $("#resend-activate-email-danger-alert").html('');
    $("#resend-activate-email-danger-alert").hide();

    $('#resend-activate-email-button')
        .html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Loading...')
        .attr('disabled', true);

    $.ajax({
        type:'POST',
        url:targetUrl,
        data:{},
        headers:{"X-CSRFToken": crf_token},
        success:function(data){
            $('#resend-activate-email-button').html('Update')
                                              .attr('disabled', false);

            console.log(data);
            if ( data.success === true )
            {
                var message = "Sent the Email successful! Reloading...";
                $("#resend-activate-email-success-alert").show();
                $("#resend-activate-email-success-alert").html(
                    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' + message
                );
                $("#resend-activate-email-success-alert").fadeTo(4000, 500).slideUp(500, function(){
                    $("#resend-activate-email-success-alert").slideUp(6000, function(){
                        const currentUrl = $('#current-page').attr("data-url");
                        window.location.href = currentUrl;
                    });
                    $("#resend-activate-email-success-alert").html('');
                    $("#resend-activate-email-success-alert").hide();
                });
            }
            else
            {
                var message = "";
                for (const [key, values] of Object.entries(data.errors))
                {
                    values.forEach(function(item, index, array) {
                        message += item + "<br>";
                    });
                }

                $("#resend-activate-email-danger-alert").html(message);
                $("#resend-activate-email-danger-alert").show();
            }
        },
        error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}
