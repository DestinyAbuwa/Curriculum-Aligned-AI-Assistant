import React from 'react';
import { Stethoscope } from 'lucide-react';

/*
  One message in the chat: a name row (with a stethoscope avatar for the
  assistant), then the message bubble.
  Assistant bubbles are light gray; your bubbles are white with a navy outline.
  If a message has "bullets" or "sources", they are listed inside the bubble.
*/

// Turns a saved timestamp into a time like "02:05 PM".
function formatTime(timestamp) {
    if (!timestamp) return '';
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function ChatMessage({ message }) {
    const isAssistant = message.sender === 'assistant';
    const time = message.time ?? formatTime(message.created_at);

    return (
        <div>
            {/* Name row */}
            <div className={`mb-3 flex items-center gap-3 ${isAssistant ? 'h-9' : 'h-4'}`}>
                {isAssistant && (
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#13294B] text-white">
                        <Stethoscope size={18} />
                    </div>
                )}
                <div className="flex items-center gap-2">
                    <span className="text-[13px] font-medium leading-4 text-[#13294B]">
                        {isAssistant ? (<><span className="text-[#D41F34]">UICOMP</span> Assistant</>) : message.author}
                    </span>
                    <span className="text-xs leading-[14px] text-[#6B7280]">{time}</span>
                </div>
            </div>

            {/* Message bubble */}
            <div className={`rounded-2xl p-4 text-[15px] leading-6 text-[#111827] ring-1 ring-inset ${
                isAssistant ? 'bg-[#F9FAFB] ring-[#E5E7EB]' : 'bg-white ring-[#13294B]'
            }`}>
                <p>{message.content}</p>

                {/* Optional bullet list */}
                {message.bullets && (
                    <ul role="list" className="mt-3 space-y-2">
                        {message.bullets.map((item) => (
                            <li key={item} className="flex items-start gap-[9px]">
                                <span className="mt-[7px] h-1 w-1 shrink-0 bg-[#13294B]" />{item}
                            </li>
                        ))}
                    </ul>
                )}

                {/* Optional "Related Documents" list */}
                {message.sources && (
                    <div className="mt-3 border-t border-[#E5E7EB] pt-[11px]">
                        <p className="text-[10px] font-bold leading-[15px] text-[#111827]">Related Documents</p>
                        <div className="mt-[2px]">
                            {message.sources.map((src, i) => (
                                <button key={src.title} type="button" className="block cursor-pointer text-left text-[10px] leading-[15px] text-[#2563EB] hover:underline">
                                    {i + 1}. {src.title} – (Slide {src.slide})
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
