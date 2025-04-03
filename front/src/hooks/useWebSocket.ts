import { useEffect, useRef, useCallback } from "react";

const useWebSocket = (url: string, onMessage: (message: any) => void) => {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<number | undefined>(undefined);
  const reconnectAttempts = useRef<number>(0);
  const MAX_RECONNECT_ATTEMPTS = 5;

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        console.log("WebSocket connection opened");
        reconnectAttempts.current = 0;
      };

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          onMessage(message);
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      ws.current.onclose = () => {
        console.log("WebSocket connection closed");
        if (reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts.current += 1;
          // Attempt to reconnect after 3 seconds
          reconnectTimeout.current = window.setTimeout(connect, 3000);
        } else {
          console.error("Max reconnection attempts reached");
          // Don't trigger the failed state, just log the error
        }
      };

      ws.current.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
    } catch (error) {
      console.error("Error creating WebSocket connection:", error);
      if (reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts.current += 1;
        // Attempt to reconnect after 3 seconds
        reconnectTimeout.current = window.setTimeout(connect, 3000);
      } else {
        console.error("Max reconnection attempts reached");
        // Don't trigger the failed state, just log the error
      }
    }
  }, [url, onMessage]);

  useEffect(() => {
    connect();

    return () => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.close();
      }
      if (reconnectTimeout.current) {
        window.clearTimeout(reconnectTimeout.current);
      }
    };
  }, [connect]);

  return ws.current;
};

export default useWebSocket;
