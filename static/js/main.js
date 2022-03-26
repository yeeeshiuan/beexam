
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
