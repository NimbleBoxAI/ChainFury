try {
  let scriptUrl = document.currentScript.src;

  function extractChatBotInfo(url) {
    const params = new URLSearchParams(new URL(url).search);
    const chatBotId = params.get('chatBotId');
    const origin = new URL(url).origin + '/';
    return { chatBotId, origin };
  }

  window.onload = function () {
    // Get the query parameter for chatbot id
    let chatBotInfo = extractChatBotInfo(scriptUrl);
    const chatbotId = chatBotInfo.chatBotId;
    // Get the base URL of the script
    const baseUrl = chatBotInfo.origin;

    // Create the chatbot toggle button
    const chatbotToggle = document.createElement('button');
    chatbotToggle.id = 'chatbot-toggle';
    chatbotToggle.style.position = 'absolute';
    chatbotToggle.style.zIndex = '10001';
    chatbotToggle.style.bottom = '12px';
    chatbotToggle.style.right = '12px';
    chatbotToggle.style.width = '80px';
    chatbotToggle.style.height = '80px';
    chatbotToggle.style.backgroundColor = 'transparent';
    chatbotToggle.style.border = '0px';
    chatbotToggle.style.cursor = 'pointer';
    document.body.appendChild(chatbotToggle);

    // Create the chatbot iframe
    const iframe = document.createElement('iframe');
    iframe.src = `${baseUrl}ui/chat/${chatbotId}#close`;
    iframe.style.borderTopLeftRadius = '8px';
    iframe.style.position = 'absolute';
    iframe.style.zIndex = '10000';
    iframe.style.bottom = '12px';
    iframe.style.right = '12px';
    iframe.style.width = '350px';
    iframe.style.height = '80px';
    document.body.appendChild(iframe);

    // Add click event listener to the chatbot toggle button
    chatbotToggle.addEventListener('click', function () {
      if (iframe.style.height === '80px') {
        iframe.style.height = '560px'; // set height when chatbot is opened
        iframe.style.width = '350px';
        iframe.src = `${baseUrl}ui/chat/${chatbotId}#open`;
      } else {
        iframe.src = `${baseUrl}ui/chat/${chatbotId}#close`;
        iframe.style.width = '100px';
        iframe.style.height = '80px'; // set height when chatbot is closed
      }
    });
  };
} catch (e) {
  console.log(e);
}
