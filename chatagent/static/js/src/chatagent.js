/* Javascript for ChatAgentXBlock. */
function ChatAgentXBlock(runtime, element) {

    function updateTextArea(log) {
        $('.chatbox', element).text(log);
    }

    function invoke(method, data, onSuccess) {
        var handlerUrl = runtime.handlerUrl(element, method);

        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(data),
            success: onSuccess
        });
    }

    invoke('print_table_content', null, function (data) {
        console.log("log: " + data['result']);
        $('.chatbox', element).text("Result: " + data['result']);
    });

    $(function ($) {
        var outputField = document.getElementById('chatbox');
        var inputField = document.getElementById('usermsg');
        inputField.focus();

        //$('chatbox').text('Hello, user');

    });

}
