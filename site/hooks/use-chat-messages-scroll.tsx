import useSWR from "swr";
import { useRef, useEffect, useCallback } from "react";

type ScrollFlag = ScrollBehavior | false;

export function useChatMessagesScroll() {
  const containerRef = useRef<HTMLDivElement>(null);
  const endRef = useRef<HTMLDivElement>(null);

  const { data: isAtTop = false, mutate: setIsAtTop } = useSWR(
    `chat-messages:is-at-top`,
    null,
    { fallbackData: false }
  );

  const { data: isAtBottom = false, mutate: setIsAtBottom } = useSWR(
    `chat-messages:is-at-bottom`,
    null,
    { fallbackData: false }
  );

  const { data: scrollBehavior = false, mutate: setScrollBehavior } =
    useSWR<ScrollFlag>(`chat-messages:should-scroll`, null, {
      fallbackData: false,
    });

  useEffect(() => {
    if (scrollBehavior) {
      endRef.current?.scrollIntoView({ behavior: scrollBehavior });
      setScrollBehavior(false);
    }
  }, [setScrollBehavior, scrollBehavior]);

  const scrollToBottom = useCallback(
    (scrollBehavior: ScrollBehavior = "smooth") => {
      setScrollBehavior(scrollBehavior);
    },
    [setScrollBehavior]
  );

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return;
    }
    const handleScroll = () => {
      // Since we're using flex-col-reverse, scrollTop of 0 means we're at the "bottom" visually (top of reversed content)
      // We want to detect when we're at the visual top (which is the end of the scroll area)
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isAtVisualTop = scrollTop + scrollHeight <= clientHeight + 5; // 5px tolerance
      setIsAtTop(isAtVisualTop);
      // Allow 5px of tolerance.
      const isAtVisualBottom = scrollTop >= 0;
      setIsAtBottom(isAtVisualBottom);
    };
    container.addEventListener("scroll", handleScroll);
    handleScroll();
  }, [containerRef]);
  return {
    containerRef,
    endRef,
    isAtTop,
    isAtBottom,
    scrollToBottom,
  };
}
