import { cn } from "@/lib/utils";
import { UIMessage } from "ai";
import { useRef } from "react";

export default function Messages({ messages }: { messages: UIMessage[] }) {
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  return (
    <div className="...">
      {messages.map(message => (
        <div key={message.id}
          className={cn(
          "w-full mx-auto max-w-3xl px-2 sm:px-4 group/message text-stone-900 dark:text-stone-300 py-2",
          {
            "flex flex-col items-end": message.role === "user",
          },
          {
            "flex flex-col items-start": message.role === "assistant",
          }
        )}>
          <div className="flex flex-row pl-4 pb-1 text-xs font-semibold text-neutral-400">{message.role === "assistant" && "JaaydenBot"}</div>
          <div
            className={cn(
              "flex flex-col gap-1.5 w-fit min-w-0 font-base max-w-[80%]",
              {"bg-blue-50 dark:bg-blue-600 rounded-xl rounded-br-sm px-4 py-1":
                message.role === "user",
              },
              {"bg-neutral-50 dark:bg-neutral-700 rounded-xl rounded-bl-sm px-4 py-1":
                message.role === "assistant",
              }
            )}
          >
          {message.parts?.map((part, index) => {
              const key = `${message.id}-${index}`;

              if (part.type === "text") {

                return (
                  <div
                    key={key}
                    className="flex flex-row gap-2 items-start relative"
                  >
                    <div
                      data-testid="message-content"
                      className="flex flex-col gap-0.5 w-full min-w-0 prose-sm prose-neutral dark:prose-invert max-w-none leading-relaxed prose-code:before:content-none prose-code:after:content-none overflow-wrap-anywhere break-words text-base"
                    >
                      {part.text}
                    </div>
                  </div>
                );
              }

              return null;
            })}
            </div>
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}