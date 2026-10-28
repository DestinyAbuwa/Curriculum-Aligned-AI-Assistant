import React from 'react';
import { Plus, PanelLeftClose, Stethoscope, LogOut } from 'lucide-react';

/*
  Left sidebar of the chat screen (navy, 280px wide, as in the Figma).
  Top to bottom: logo and name, New Chat + close buttons, the list of past
  chats, and a status card with the signed-in user and a Log out button.
  When isOpen is false it slides closed to zero width.
*/

// Turns a thread's saved time into a short label:
// a time like "02:05 PM" for today, or a date like "Oct 21" for older chats.
function formatThreadDate(thread) {
    if (thread.date) return thread.date;
    if (!thread.created_at) return '';

    const created = new Date(thread.created_at);
    const isToday = created.toDateString() === new Date().toDateString();
    return isToday
        ? created.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        : created.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

export function Sidebar({ isOpen, onClose, threads, activeThreadId, onSelectThread, onNewChat, user, onLogout }) {
    return (
        <aside
            className={`flex shrink-0 flex-col overflow-hidden bg-[#13294B] pb-6 pt-6 transition-all duration-300 ease-in-out ${
                isOpen ? 'w-[280px] px-5 opacity-100' : 'pointer-events-none w-0 px-0 opacity-0'
            }`}
        >
            {/* Fixed-width inner column so the content doesn't squash while the sidebar slides */}
            <div className="flex h-full w-[240px] flex-col">

                {/* Logo and app name */}
                <div className="flex items-center gap-2.5">
                    <img src="/uic-logo.png" alt="UIC" className="h-10 w-10 shrink-0 rounded-full object-cover" />
                    <div className="min-w-0">
                        <h2 className="text-base font-semibold leading-[1.3] text-white">UICOMP Assistant</h2>
                        <p className="text-xs leading-[18px] text-white/70">Medical Education &amp; Curriculum</p>
                    </div>
                </div>

                {/* New Chat button, and the button that closes the sidebar */}
                <div className="mt-4 flex gap-2">
                    <button
                        type="button"
                        onClick={onNewChat}
                        className="flex h-[41px] flex-1 cursor-pointer items-center gap-1.5 rounded-xl bg-[#D41F34] pl-[13px] text-sm font-semibold text-white transition-colors hover:bg-[#BC1A2D]"
                    >
                        <Plus size={17} /> New Chat
                    </button>
                    <button
                        type="button"
                        onClick={onClose}
                        aria-label="Close sidebar"
                        title="Close sidebar"
                        className="flex h-[41px] w-[41px] shrink-0 cursor-pointer items-center justify-center rounded-xl bg-[#D41F34] text-white transition-colors hover:bg-[#BC1A2D]"
                    >
                        <PanelLeftClose size={18} />
                    </button>
                </div>

                {/* List of past chats */}
                <p className="mt-6 text-xs font-semibold uppercase leading-4 text-white/50">Conversation History</p>
                <div className="mt-[11px] flex-1 space-y-3 overflow-y-auto pb-4">
                    {threads.length === 0 ? (
                        <p className="text-xs leading-4 text-white/50">No chat history</p>
                    ) : (
                        threads.map((thread) => {
                            const isActive = activeThreadId === thread.id;
                            return (
                                <button
                                    key={thread.id}
                                    type="button"
                                    onClick={() => onSelectThread(thread.id)}
                                    className={`flex w-full cursor-pointer items-center gap-3 rounded-[14px] p-3 text-left transition-colors ${
                                        isActive ? 'bg-white/[0.07]' : 'hover:bg-white/5'
                                    }`}
                                >
                                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white/[0.08] text-white">
                                        <Stethoscope size={18} />
                                    </div>
                                    {/* Title and date share the top row; the preview sits under the title */}
                                    <div className="grid min-w-0 flex-1 grid-cols-[minmax(0,1fr)_auto] gap-x-2">
                                        <h3 className="line-clamp-2 break-words text-sm font-semibold leading-[17px] text-white">{thread.title}</h3>
                                        <span className="self-end text-[11px] leading-4 text-white/50">{formatThreadDate(thread)}</span>
                                        <p className="col-start-1 mt-1 truncate text-xs leading-[15px] text-white/70">{thread.preview}</p>
                                    </div>
                                </button>
                            );
                        })
                    )}
                </div>

                {/* Status card: app name, online dot, who is signed in, and Log out */}
                <div className="shrink-0 rounded-2xl bg-white/[0.06] p-4">
                    <p className="text-sm font-semibold leading-[17px] text-white">UICOMP Curriculum AI Assistant</p>
                    <p className="mt-1 text-xs leading-[15px] text-white/70">College of Medicine curriculum guidance</p>
                    <div className="mt-3 flex items-center justify-between">
                        <div className="flex items-center gap-1.5 text-[11px] font-medium leading-[13px] text-white/80">
                            <span className="h-1.5 w-1.5 rounded-full bg-[#10B981]" /> Online
                        </div>
                        <button
                            type="button"
                            onClick={onLogout}
                            className="flex cursor-pointer items-center gap-1 text-[11px] font-medium leading-[13px] text-white/70 transition-colors hover:text-white"
                        >
                            <LogOut size={13} /> Log out
                        </button>
                    </div>
                    {user?.email && (
                        <p className="mt-2 truncate text-[11px] leading-4 text-white/50">Signed in as {user.email}</p>
                    )}
                </div>
            </div>
        </aside>
    );
}
