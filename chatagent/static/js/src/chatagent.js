/* Javascript for ChatAgentXBlock. */
function ChatAgentXBlock(runtime, element) {
    /**
     * HTML newline used in the chatbox
     * @const
     */
    var HTML_NEWLINE = "<p />";
    /**
     * The name of the Chat Agent (With HTML formatting for display in the chatbox).
     * @const
     */
    var CHAT_AGENT_NAME = "<strong>Mimmi:</strong> ";
    /**
     * The HTML id of the users input field
     * @const
     */
    var USER_INPUT_FIELD_ID = "#userInput";
    /**
     * The HTML id of the <div> containing the chatbox output field
     * @const
     */
    var CHATBOX_ID = "#chatbox";
    /**
     * The name of the currently active user of this application.
     * The value of USER_NAME is set in the function `getAndSetUsername`.
     * Marked as const, because it is not intended for this to be changed (except in `getAndSetUsername`).
     * @see #getAndSetUsername
     */
    var USER_NAME = "";
    /**
     * Variable for if the welcome message has been displayed yet.
     */
    var is_welcome_msg_shown = false;

    /**
     * Prints the default welcome message into the chatbox. This should only be called once
     * (on pageload, or when chatbox is cleared of all content)
     */
    function getDefaultWelcomeMessage() {
        var message = "";
        var username = {'username': USER_NAME};
        invoke('get_default_welcome_message', username, function (data) {
            message = CHAT_AGENT_NAME + data['welcome_msg'];
            $(CHATBOX_ID).append(message);
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
     * Updates the chatbox with the users input and the results from the Chat Agent.
     * The results are based on the passed input from the user.
     * @param screenname {string} User name
     * @param input {string} User input
     */
    function updateChatLog(screenname, input) {
        /*
         TODO:
         - Ask user for confirmation (Correct answer: Yes, No, New question)
         */
        var title = "";
        var chatlog = "";
        var response = "";
        var disableLink = false;
        var is_input_no = false;
        var is_input_yes = false;
        var shouldInputBeYesOrNo = false;
        if (shouldInputBeYesOrNo) {
            is_input_no = (input.toLowerCase() == "n" || input.toLowerCase() == "no");
            is_input_yes = (input.toLowerCase() == "y" || input.toLowerCase() == "yes");
        } //if
        //add the users input to the chatbot
        $(CHATBOX_ID).append(screenname);
        $(CHATBOX_ID).append(input);
        $(CHATBOX_ID).append(HTML_NEWLINE);
        // quick & dirty test code: should answer be yes or no?
        if (shouldInputBeYesOrNo && !is_input_yes && !is_input_no) {
            chatlog = CHAT_AGENT_NAME + "Is this the question you are looking for?";
            chatlog += HTML_NEWLINE + " Please enter 'Yes' or 'No'." + HTML_NEWLINE;
            $(CHATBOX_ID).append(chatlog);
        } else if (shouldInputBeYesOrNo && is_input_yes) {
            //use default edx question
            //show rest of answer
            console.log("answer is yes");
        } else if (shouldInputBeYesOrNo && is_input_no) {
            //ask user for input/question
            //ask user if question should be re-phrased
            //ask user if next answer should be retrieved
            console.log("answer is no");
        } else {
            //create JSON format for input
            var json_input = {'user_input': input};
            invoke('handle_user_input', json_input, function (data) {
                title = data['title'];
                response = data['response'];
                disableLink = data['disable_link'];
                //check if links should be removed, and if the answer contains hyperlink
                if (disableLink && response.indexOf("<a ") >= 0) {
                    //remove first occurrence of <a>
                    response = $(response + " a:first").text();
                } //if
                chatlog = CHAT_AGENT_NAME + title + response + HTML_NEWLINE;
                console.log(chatlog);
                $(CHATBOX_ID).append(chatlog);
            }); //invoke
        } //if
    } //updateChatLog

    /**
     * Invoke function for retrieving data from the Edx XBlock.
     * @param method {string} Name of function to call from XBlocks
     * @param data {object} Data to process || null
     * @param onSuccess {function (data)} Action to execute on sucessfull POST (e.g. data processing)
     */
    function invoke(method, data, onSuccess) {
        var statusCode = 0;
        var errorMsg = 0;
        var handlerUrl = runtime.handlerUrl(element, method);
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(data),
            success: onSuccess,
            statusCode: {
                404: function() {
                    statusCode = 404;
                    errorMsg = statusCode + ": This page does not exist.";
                    console.log(errorMsg)
                }, //404
                500: function() {
                    statusCode = 500;
                    errorMsg = statusCode + ": Internal Server Error.";
                    console.log(errorMsg);
                    $(CHATBOX_ID).append(CHAT_AGENT_NAME + " " + errorMsg + HTML_NEWLINE);
                } //500
            } //statuscode
        }); //$.ajax
    } //invoke

    $(function ($) {
        //get the username and set focus in the message field
        getAndSetUsername();
        $(USER_INPUT_FIELD_ID).focus();

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
            var input = $(USER_INPUT_FIELD_ID).val();
            var screenname = USER_NAME + ": ";
            if (input != "") {
                input = $(USER_INPUT_FIELD_ID).val();
                updateChatLog(screenname, input);
                $(USER_INPUT_FIELD_ID).attr('value', "");
                $(USER_INPUT_FIELD_ID).focus();
            } //if
            return false;
        }); //$('#btnSubmit')

    }); //$(function ($)

} //ChatAgentXBlock
