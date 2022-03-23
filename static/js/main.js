
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
        success:function(json){
            console.log(json);
        },
        error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}
