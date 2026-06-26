import { SendHorizonal } from "lucide-react";
import { FormEvent, useState } from "react";

interface AIInputProps {
  placeholder?: string;
  compact?: boolean;
  onSend: (message: string) => void;
}

export function AIInput({ placeholder = "Ask ATLAS naturally...", compact = false, onSend }: AIInputProps) {
  const [value, setValue] = useState("");

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const message = value.trim();
    if (!message) {
      return;
    }
    onSend(message);
    setValue("");
  };

  return (
    <form className="flex gap-2" onSubmit={submit}>
      <textarea
        className={compact ? "atlas-textarea min-h-[44px] flex-1" : "atlas-textarea flex-1"}
        placeholder={placeholder}
        value={value}
        rows={compact ? 1 : 3}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            submit(event);
          }
        }}
      />
      <button className="atlas-button h-auto self-stretch" type="submit" aria-label="Send message">
        <SendHorizonal className="h-4 w-4" aria-hidden="true" />
      </button>
    </form>
  );
}
