/* Javascript for ChatAgentXBlock. */
function ChatAgentXBlock(runtime, element) {
    /**
    * The name of the currently active user of this application.
    * The value of USER_NAME is set in the function `getAndSetUsername`.
    * Marked as const, because it is not intended for this to be changed (except in `getAndSetUsername`).
    * @see #getAndSetUsername
    * @const
    */
    var USER_NAME = "";
    /**
    * HTML newline used in the chatbox
    * @const
    */
    var HTML_NEWLINE = "<p />";
    /**
    * The name of the Chat Agent, with HTML formatting for display in the chatbox.
    * @const
    */
    var CHAT_AGENT_NAME = "<strong>Mimmi:</strong> ";
    /**
    * Variable for if the welcome message has been displayed yet.
    */
    is_welcome_msg_shown = false;

    /**
    * Prints the default welcome message into the chatbox. This should only be called once
    * (on pageload, or when chatbox is cleared of all content)
    */
    function getDefaultWelcomeMessage() {
        var message = "";
        username = {'username': USER_NAME};
        console.log(username);
        invoke('get_default_welcome_message', username, function (data) {
            message = CHAT_AGENT_NAME + data['welcome_msg'];
            $('.chatbox').append(message);
        }); //invoke
    } //getDefaultWelcomeMessage

    /**
    * This function retrieves the username from the HTML element in which it were set,
    * and if the username is not set, it is retrieved by calling the `invoke` function.
    */
    function getAndSetUsername() {
        USER_NAME = $('.username').val();
        if (USER_NAME == "") {
            invoke('get_username', null, function (data) {
                USER_NAME = data['username'];
                $('.username').text(USER_NAME);
                //has the welcome message been shown?
                if (!is_welcome_msg_shown) {
                    getDefaultWelcomeMessage();
                } //if
            }); //invoke
        } //if
    } //getAndSetUsername

    /**
    * Updates the chatbox with the users input and the results from the Chat Agent,
    * based on the passed input.
    * @param screenname {string} User name
    * @param input {string} User input
    */
    function updateChatLog(screenname, input) {
        /*
            TODO:
            - Handle and store input (e.g. lookup question, find answers, store in db)
            - Retrieve results and add to chatbox
            - Ask user for confirmation (Correct answer: Yes, No, New question)
        */
        //add the users input to the chatbot
        $('.chatbox').append(screenname);
        $('.chatbox').append(input);
        $('.chatbox').append(HTML_NEWLINE);
        //create JSON format for input
        json_input = {'user_input': input};
        console.log(input)
        invoke('handle_user_input', json_input, function (data) {
            var chatlog = CHAT_AGENT_NAME + data['result'] + HTML_NEWLINE;
            $('.chatbox').append(chatlog);
            //TODO: Remove and replace these later on
            var links = $(".chatbox a").map(function() {
                return this.href;
            }).get();
            //get the last link that were added
            last_link = links[links.length-1];
            //open the selected link
            $(".chatbox a").click(function() {
                console.log("href is: " + last_link);
                window.open(last_link, '_blank');
            }); //$(".chatbox a")
        }); //invoke
    } //updateChatLog

    /**
    * Invoke function for retrieving data from the Edx XBlock.
    * @param method {string} Name of function to call from XBlocks
    * @param data {object} Data to process || null
    * @param onSuccess {function (data)} Action to execute on sucessfull POST (e.g. data processing)
    */
    function invoke(method, data, onSuccess) {
        var handlerUrl = runtime.handlerUrl(element, method);
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(data),
            success: onSuccess
        }); //$.ajax
    } //invoke

    $(function ($) {
        //get the username and set focus in the message field
        getAndSetUsername();
        $('#userInput').focus();

        //exit the chat agent
        $('#exit').click(function(){
            var confirmMsg = "Are you sure you want to end the session?";
            var exit = confirm(confirmMsg);
                if(exit == true){
                    //TODO: close window or re-direct user back to course page
                } //if
        }); //$('#exit')

        //send a new message to the chat agent
        $('#btnSubmit').click(function() {
            var input = $('#userInput').val();
            var screenname = USER_NAME + ": ";
            if (input != "") {
                input = $('#userInput').val();
                updateChatLog(screenname, input);
                $('#userInput').attr('value', "");
                $('#userInput').focus();
            } //if
            return false;
        }); //$('#btnSubmit')

    }); //$(function ($)

} //ChatAgentXBlock
