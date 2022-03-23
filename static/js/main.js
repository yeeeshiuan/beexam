
function post_signup(e){
    e.preventDefault();
    const form = $('#signup-form')[0];
    const email = form.elements.email.value;
    const password = form.elements.password.value;
    const password_check = form.elements.password_check.value;
    const postUrl = $('#post-user-url').attr("data-url");
    $.ajax({
        type:'POST',
        url:postUrl,
        data:{
            email:email,
            password:password,
            password_check:password_check,
        },
        success:function(data){
            console.log(data);
            if ( data.email === email )
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
                $("#signup-danger-alert").show();
                $("#signup-danger-alert").html(data.error);
                $("#signup-danger-alert").fadeTo(4000, 500).slideUp(500, function(){
                    $("#signup-danger-alert").slideUp(500);
                    $("#signup-danger-alert").html('');
                    $("#signup-danger-alert").hide();
                });
            }
        },
        error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}
