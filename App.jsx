import React, { useState, useRef, useEffect } from 'react';
import {
    Plus, 
    Paperclip,
    Mic,
    ArrowUp,
    User,
    PanelLeftClose,
    PanelLeftOpen
} from 'lucide-react';

export default function App() {
    const [inputMessage, setInputMessage] = useState('');
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const messagesEndRef = useRef(null);

    // Initial message default setup
    const initialMessages = [
        {
            id: 'welcome-msg',
            sender: 'assistant',
            author: 'UICOMP Assistant',
            time: '10:02 AM',
            content: 'Welcome to the UICOMP Curriculum Assistant. Ask questions about lecture slides, clinical guidelines, course syllabi, or exam preparation topics.'
        }
    ];

    // Dynamic threads array initialized with default welcome message
    const [threads, setThreads] = useState([
        {
            id: 'default-thread',
            title: 'Welcome Chat',
            preview: 'Welcome to the UICOMP Curriculum Assistant...',
            date: 'Today',
            messages: initialMessages
        }
    ]);
    const [activeThreadId, setActiveThreadId] = useState('default-thread');

    const activeThread = threads.find((t) => t.id === activeThreadId);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (activeThread?.messages?.length) {
            scrollToBottom();
        }
    }, [activeThread?.messages]);

    const createNewChat = () => {
        const newThreadId = Date.now().toString();

        const newThread = {
            id: newThreadId,
            title: 'New Chat',
            preview: 'No messages yet',
            date: 'Just now',
            messages: initialMessages
        };

        setThreads((prev) => [newThread, ...prev]);
        setActiveThreadId(newThreadId);
        return newThreadId;
    };

    const handleSendMessage = (e) => {
        e.preventDefault();
        if (!inputMessage.trim()) return;

        let currentId = activeThreadId;

        if (!currentId) {
            currentId = createNewChat();
        }

        const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const userText = inputMessage.trim();

        const newUserMessage = {
            id: Date.now().toString(),
            sender: 'user',
            author: 'You',
            time: currentTime,
            content: userText
        };

        setThreads((prevThreads) =>
            prevThreads.map((thread) => {
                if (thread.id === currentId) {
                    const isDefaultTitle = thread.title === 'New Chat' || thread.title === 'Welcome Chat';
                    const newTitle = isDefaultTitle ? userText : thread.title;

                    return {
                        ...thread,
                        title: newTitle,
                        preview: userText,
                        messages: [...thread.messages, newUserMessage]
                    };
                }
                return thread;
            })
        );

        setInputMessage('');
    };

    return (
        <div className="flex h-screen w-full bg-white text-[#111827] overflow-hidden" style={{ fontFamily: "Inter, system-ui, -apple-system, sans-serif" }}>
            
            {/* Collapsible Sidebar */}
            <aside 
                className={`flex shrink-0 flex-col bg-[#0F2942] transition-all duration-300 ease-in-out ${
                    isSidebarOpen ? 'w-[260px] px-4 pb-5 pt-5 opacity-100' : 'w-0 px-0 pb-0 pt-0 opacity-0 pointer-events-none'
                }`}
            >
                <div className="flex w-[228px] flex-col h-full">
                    {/* Header with Toggle Button */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#E11D48] font-bold text-white text-[11px]">
                                UIC
                            </div>
                            <div>
                                <h2 className="text-[13px] font-bold leading-tight text-white">UICOMP Assistant</h2>
                                <p className="text-[10px] text-blue-200/70">Medical Education &amp; Curriculum</p>
                            </div>
                        </div>
                        <button 
                            onClick={() => setIsSidebarOpen(false)}
                            className="text-white/60 hover:text-white transition-colors p-1 rounded-md hover:bg-white/10"
                            title="Close Sidebar"
                        >
                            <PanelLeftClose size={18} />
                        </button>
                    </div>

                    {/* New Chat Button */}
                    <div className="mt-4">
                        <button 
                            onClick={createNewChat} 
                            className="flex h-9 w-full cursor-pointer items-center gap-1.5 rounded-lg bg-[#E11D48] px-3 text-xs font-semibold text-white transition-colors hover:bg-[#be123c]"
                        >
                            <Plus size={15} /> New Chat
                        </button>
                    </div>

                    {/* History Heading */}
                    <p className="mt-5 text-[10px] font-semibold uppercase tracking-wider text-white/40">CONVERSATION HISTORY</p>

                    {/* Threads List */}
                    <div className="mt-2 flex-1 space-y-2 overflow-y-auto pr-0.5">
                        {threads.length === 0 ? (
                            <p className="mt-4 text-center text-[11px] italic text-white/30">No chat history</p>
                        ) : (
                            threads.map((thread) => {
                                const isActive = activeThreadId === thread.id;
                                return (
                                    <button
                                        key={thread.id}
                                        type="button"
                                        onClick={() => setActiveThreadId(thread.id)}
                                        className={`flex w-full cursor-pointer items-start gap-2.5 rounded-xl p-2.5 text-left transition-colors ${
                                            isActive ? 'bg-[#1E3A5F]' : 'hover:bg-white/5'
                                        }`}
                                    >
                                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-white/10 text-white mt-0.5">
                                            <User size={13} />
                                        </div>
                                        <div className="min-w-0 flex-1">
                                            <div className="flex items-center justify-between gap-1">
                                                <h3 className="truncate text-xs font-semibold text-white">{thread.title}</h3>
                                                <span className="shrink-0 text-[9px] text-white/40">{thread.date}</span>
                                            </div>
                                            <p className="mt-0.5 truncate text-[10px] text-white/50">{thread.preview}</p>
                                        </div>
                                    </button>
                                );
                            })
                        )}
                    </div>

                    {/* Bottom Card */}
                    <div className="mt-auto shrink-0 rounded-xl bg-[#1E3A5F]/60 p-3">
                        <p className="text-xs font-bold leading-tight text-white">UICOMP Curriculum AI Assistant</p>
                        <p className="mt-1 text-[10px] text-white/60">College of Medicine curriculum guidance</p>
                        <div className="mt-2 flex items-center gap-1.5 text-[10px] font-medium text-white/80">
                            <span className="h-1.5 w-1.5 rounded-full bg-[#10B981]" /> Online
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex min-w-0 flex-1 flex-col h-full overflow-hidden px-8 pb-4 pt-6 bg-white relative">
                
                {/* Header Section */}
                <header className="relative flex flex-col items-center shrink-0">
                    {!isSidebarOpen && (
                        <button 
                            onClick={() => setIsSidebarOpen(true)}
                            className="absolute left-0 top-0 p-1.5 rounded-md text-[#0F2942] hover:bg-slate-100 transition-colors"
                            title="Open Sidebar"
                        >
                            <PanelLeftOpen size={20} />
                        </button>
                    )}
                    <h1 
                        className="font-bold tracking-tight text-base md:text-lg" 
                        style={{ color: '#0F2942' }}
                    >
                        UICOMP Curriculum AI Assistant
                    </h1>
                    <p className="mt-0.5 text-xs text-[#94A3B8]">
                        UICOMP Medical Education &amp; Curriculum Knowledge Base
                    </p>
                </header>

                {/* Chat Message Area */}
                <div className="mt-6 flex-1 overflow-y-auto">
                    {activeThread && activeThread.messages.length > 0 ? (
                        <div className="mx-auto w-full max-w-[680px] space-y-5 pb-4">
                            {activeThread.messages.map((msg) => {
                                const isAssistant = msg.sender === 'assistant';
                                return (
                                    <div key={msg.id} className="space-y-1.5">
                                        {/* Avatar & Header Info */}
                                        <div className="flex items-center gap-2">
                                            <div className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-white ${
                                                isAssistant ? 'bg-[#0F2942]' : 'bg-[#E11D48]'
                                            }`}>
                                                <User size={12} />
                                            </div>
                                            <span className="text-xs font-bold text-[#1E293B]">
                                                {msg.author}
                                            </span>
                                            <span className="text-[10px] text-[#94A3B8]">
                                                {msg.time}
                                            </span>
                                        </div>

                                        {/* Message Container */}
                                        <div className={`rounded-2xl p-4 text-xs leading-relaxed ${
                                            isAssistant 
                                                ? 'bg-[#F8F9FA] text-[#334155]' 
                                                : 'bg-white border border-[#E11D48]/40 text-[#1E293B] shadow-sm'
                                        }`}>
                                            <p>{msg.content}</p>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        <div className="flex h-full items-center justify-center text-[#94A3B8] text-xs">
                            Start a conversation by typing a message below.
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <form onSubmit={handleSendMessage} className="mx-auto w-full max-w-[680px] shrink-0 pt-2">
                    <div className="flex h-12 items-center gap-3 rounded-full bg-[#F1F5F9] px-4 shadow-inner">
                        <button type="button" className="text-[#94A3B8] hover:text-[#64748B]">
                            <Paperclip size={16} />
                        </button>
                        <input
                            type="text"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            placeholder="Ask a question..."
                            className="min-w-0 flex-1 bg-transparent text-xs text-[#1E293B] outline-none placeholder:text-[#94A3B8]"
                        />
                        <button type="button" className="text-[#94A3B8] hover:text-[#64748B]">
                            <Mic size={16} />
                        </button>
                        <button 
                            type="submit" 
                            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#E11D48] text-white hover:bg-[#be123c] transition-colors"
                        >
                            <ArrowUp size={15} />
                        </button>
                    </div>
                    <p className="mt-2 text-center text-[10px] text-[#94A3B8]">
                        Official UICOMP Internal Medical Education Assistant — Answers generated strictly from verified course materials.
                    </p>
                </form>
            </main>
        </div>
    );
}