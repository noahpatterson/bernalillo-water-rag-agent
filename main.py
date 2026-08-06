import os
from dotenv import load_dotenv
from embedder import Embedder

def main():
    load_dotenv()
    
    onnx_execution_provider = os.getenv("ONNX_EXECUTION_PROVIDER")
    embedder = Embedder(execution_provider=onnx_execution_provider)

    print(embedder.encode("Hello, world!"))


if __name__ == "__main__":
    main()
