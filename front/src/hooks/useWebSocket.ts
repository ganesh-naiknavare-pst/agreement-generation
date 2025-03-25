import { useEffect, useRef } from "react";

const useWebSocket = (url: string, onMessage: (message: any) => void) => {
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log("WebSocket connection opened");
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      onMessage(message);
    };

    ws.current.onclose = () => {
      console.log("WebSocket connection closed");
    };

    return () => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.close();
      }
    };
  }, [url, onMessage]);

  return ws.current;
};

export default useWebSocket;
