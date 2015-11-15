/* Javascript for ChatAgentXBlock. */
function ChatAgentXBlock(runtime, element) {

    $(function ($) {
        var outputField = document.getElementById('chatbox');
        var inputField = document.getElementById('usermsg');
        inputField.focus();
         $('chatbox').text('Hello, user');
    });

}
