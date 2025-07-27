'use client';

import { useChat } from '@ai-sdk/react';
import { useState } from 'react';
import Messages from './messages';

export default function Chat() {
  const [input, setInput] = useState('');
  const { messages, sendMessage } = useChat();
  return (
    <div className="flex flex-col w-full max-w-md py-24 mx-auto stretch">

    <Messages messages={messages} />

      <form
        onSubmit={e => {
          e.preventDefault();
          sendMessage({ text: input });
          setInput('');
        }}
      >
        <input
          className="fixed dark:bg-zinc-900 bottom-0 w-full max-w-md p-2 mb-8 border border-zinc-300 dark:border-zinc-800 rounded shadow-xl"
          value={input}
          placeholder="Ask anything"
          onChange={e => setInput(e.currentTarget.value)}
        />
      </form>
    </div>
  );
}