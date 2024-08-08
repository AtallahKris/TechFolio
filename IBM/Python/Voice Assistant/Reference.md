## Important Commands

You'll need to run these commands every time you wish to make a new change to one of the files:

```bash
# Build the Docker image
docker build . -t voice-chatapp-powered-by-openai

# Run the Docker container
docker run -p 8000:8000 voice-chatapp-powered-by-openai
```

> [!NOTE]
> You can find the original code at the following link:
> [Original Code Repository](https://github.com/arora-r/chatapp-with-voice-and-openai-outline)
