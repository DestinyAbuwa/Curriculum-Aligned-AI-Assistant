import React from 'react';
import { Paperclip, Mic, ArrowUp } from 'lucide-react';

/*
  Message bar at the bottom of the chat screen: a rounded gray pill with a
  paperclip, the text box, a mic, and the red send button, plus a disclaimer.
  The paperclip and mic don't do anything yet.
*/
export function ChatInput({ value, onChange, onSubmit, placeholder = "Ask a question..." }) {
    return (
        <form onSubmit={onSubmit} className="mx-auto w-full max-w-[936px] shrink-0 border-t border-[#E5E7EB] pt-[15px]">
            <div className="mx-auto w-full max-w-[888px]">
                <div className="flex h-14 items-center gap-4 rounded-full bg-[#F4F4F6] pl-[21px] pr-4">
                    <button type="button" aria-label="Attach a file" className="shrink-0 cursor-pointer text-[#6B7280] transition-colors hover:text-[#4B5563]">
                        <Paperclip size={18} />
                    </button>
                    <input
                        type="text"
                        value={value}
                        onChange={(e) => onChange(e.target.value)}
                        placeholder={placeholder}
                        className="min-w-0 flex-1 bg-transparent text-sm text-[#111827] outline-none placeholder:text-[#6B7280]"
                    />
                    <button type="button" aria-label="Voice input" className="shrink-0 cursor-pointer text-[#6B7280] transition-colors hover:text-[#4B5563]">
                        <Mic size={19} />
                    </button>
                    <button
                        type="submit"
                        aria-label="Send message"
                        className="flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-full bg-[#D41F34] text-white transition-colors hover:bg-[#BC1A2D]"
                    >
                        <ArrowUp size={17} />
                    </button>
                </div>
                <p className="mt-2.5 text-center text-[11px] leading-[15px] text-[#6B7280]">
                    Official UICOMP Internal Medical Education Assistant — Answers generated strictly from verified course materials.
                </p>
            </div>
        </form>
    );
}
