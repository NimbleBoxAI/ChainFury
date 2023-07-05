CHATBOT_NAME="foofoo-auto-test"

echo "######\n>       python3 -m stories.api chatbot story\n######" && python3 -m stories.api chatbot story "$CHATBOT_NAME"
echo "######\n>       python3 -m stories.api fury story\n######" && python3 -m stories.api fury story
