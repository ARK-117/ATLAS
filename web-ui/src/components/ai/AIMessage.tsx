import type { AssistantMessage } from "../../types";

interface AIMessageProps {
  message: AssistantMessage;
}

export function AIMessage({ message }: AIMessageProps) {
  const isUser = message.role === "user";

  return (
    <article className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[88%] rounded-md border px-3 py-2 text-sm leading-6 ${
          isUser
            ? "border-atlas-blue/40 bg-atlas-blue/10 text-atlas-text"
            : "border-atlas-line bg-white/[0.03] text-atlas-text"
        }`}
      >
        <div className="mb-1 flex items-center justify-between gap-3 text-xs text-atlas-muted">
          <span>{isUser ? "You" : "ATLAS"}</span>
          <span className="font-mono">{message.timestamp}</span>
        </div>
        <p className="whitespace-pre-line">{message.content}</p>
      </div>
    </article>
  );
}
