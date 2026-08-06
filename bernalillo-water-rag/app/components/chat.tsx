'use client';
import { useEveAgent } from 'eve/react';
export function Chat() {
  const agent = useEveAgent();
  const isBusy = agent.status === 'submitted' || agent.status === 'streaming';
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        const message = String(form.get('message') ?? '').trim();
        if (message.length > 0) {
          void agent.send(message);
        }
      }}
    >
      {agent.data.messages.map((message) => (
        <article key={message.id}>
          <header>{message.role}</header>
          {message.parts.map((part, index) =>
            part.type === 'text' ? <p key={index}>{part.text}</p> : null,
          )}
        </article>
      ))}
      <input name="message" disabled={isBusy} className="border-2 border-gray-300 rounded-md p-2" />
      <button disabled={isBusy} type="submit">
        Send
      </button>
    </form>
  );
}
