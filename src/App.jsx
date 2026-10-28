import React, { useState, useRef, useEffect } from 'react';
import { supabase } from './supabaseClient';
import { AuthPage } from './components/AuthPage';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';

export default function App() {
    const [user, setUser] = useState(null);
    const [loadingAuth, setLoadingAuth] = useState(true);
    const [inputMessage, setInputMessage] = useState('');
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [threads, setThreads] = useState([]);
    const [activeThreadId, setActiveThreadId] = useState(null);
    const [messages, setMessages] = useState([]);
    const messagesEndRef = useRef(null);

    // 1. Listen for Supabase Authentication state changes on load
    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            setUser(session?.user ?? null);
            setLoadingAuth(false);
        });

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            setUser(session?.user ?? null);
            setLoadingAuth(false);
        });

        return () => subscription.unsubscribe();
    }, []);

    // 2. Fetch all threads belonging to the logged-in user
    useEffect(() => {
        if (!user) {
            setThreads([]);
            setActiveThreadId(null);
            return;
        }

        async function loadThreads() {
            const { data, error } = await supabase
                .from('threads')
                .select('*')
                .order('created_at', { ascending: false });

            if (!error && data) {
                setThreads(data);
                if (data.length > 0 && !activeThreadId) {
                    setActiveThreadId(data[0].id);
                }
            }
        }

        loadThreads();
    }, [user]);

    // 3. Fetch messages whenever the active thread changes
    useEffect(() => {
        if (!activeThreadId) {
            setMessages([]);
            return;
        }

        async function loadMessages() {
            const { data, error } = await supabase
                .from('messages')
                .select('*')
                .eq('thread_id', activeThreadId)
                .order('created_at', { ascending: true });

            if (!error && data) {
                setMessages(data);
            }
        }

        loadMessages();
    }, [activeThreadId]);

    // Auto-scroll to the bottom when new messages load
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Create a new chat thread in Supabase
    const handleNewChat = async () => {
        if (!user) return;

        const { data, error } = await supabase
            .from('threads')
            .insert([
                {
                    user_id: user.id,
                    title: 'New Chat',
                    preview: 'Ask a question...'
                }
            ])
            .select()
            .single();

        if (!error && data) {
            setThreads((prev) => [data, ...prev]);
            setActiveThreadId(data.id);
            setMessages([]);
        }
    };

    // Send a message and save to Supabase
    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!inputMessage.trim() || !user) return;

        let currentThreadId = activeThreadId;

        // If no active thread exists, create one first
        if (!currentThreadId) {
            const { data: newThread, error: threadError } = await supabase
                .from('threads')
                .insert([
                    {
                        user_id: user.id,
                        title: inputMessage.trim(),
                        preview: inputMessage.trim()
                    }
                ])
                .select()
                .single();

            if (threadError || !newThread) return;

            currentThreadId = newThread.id;
            setThreads((prev) => [newThread, ...prev]);
            setActiveThreadId(currentThreadId);
        }

        const userText = inputMessage.trim();
        setInputMessage('');

        // Insert User Message into Supabase
        const { data: userMsg, error: msgError } = await supabase
            .from('messages')
            .insert([
                {
                    thread_id: currentThreadId,
                    sender: 'user',
                    author: 'You',
                    content: userText
                }
            ])
            .select()
            .single();

        if (!msgError && userMsg) {
            setMessages((prev) => [...prev, userMsg]);
        }

        // Update Thread preview text & title
        await supabase
            .from('threads')
            .update({ preview: userText, title: userText })
            .eq('id', currentThreadId);

        setThreads((prev) =>
            prev.map((t) => (t.id === currentThreadId ? { ...t, preview: userText, title: userText } : t))
        );

        // Simulated Assistant Response (Replace with your actual RAG/AI backend API call)
        setTimeout(async () => {
            const assistantText = `This is a response generated for your query: "${userText}".`;
            const { data: assistantMsg } = await supabase
                .from('messages')
                .insert([
                    {
                        thread_id: currentThreadId,
                        sender: 'assistant',
                        author: 'UICOMP Assistant',
                        content: assistantText
                    }
                ])
                .select()
                .single();

            if (assistantMsg) {
                setMessages((prev) => [...prev, assistantMsg]);
            }
        }, 1000);
    };

    const handleLogout = async () => {
        await supabase.auth.signOut();
        setUser(null);
    };

    if (loadingAuth) {
        return (
            <div className="flex h-screen w-full items-center justify-center bg-white text-[#13294B]">
                <p className="text-[13px] font-semibold animate-pulse">Loading UICOMP Assistant...</p>
            </div>
        );
    }

    if (!user) {
        return <AuthPage onLoginSuccess={(userData) => setUser(userData)} />;
    }

    return (
        <div className="flex h-screen w-full bg-white text-[#111827] overflow-hidden">
            <Sidebar 
                isOpen={isSidebarOpen}
                onClose={() => setIsSidebarOpen(false)}
                threads={threads}
                activeThreadId={activeThreadId}
                onSelectThread={setActiveThreadId}
                onNewChat={handleNewChat}
                user={user}
                onLogout={handleLogout}
            />

            <main className="flex min-w-0 flex-1 flex-col h-full overflow-hidden px-8 pb-4 pt-6 bg-white relative">
                <Header 
                    isSidebarOpen={isSidebarOpen}
                    onOpenSidebar={() => setIsSidebarOpen(true)}
                    title="UICOMP Curriculum AI Assistant"
                    subtitle="UICOMP Medical Education & Curriculum Knowledge Base"
                />

                <div className="mt-[22px] flex-1 overflow-y-auto">
                    {messages.length > 0 ? (
                        <div className="mx-auto w-full max-w-[700px] space-y-5 pb-5">
                            {messages.map((msg) => (
                                <ChatMessage key={msg.id} message={msg} />
                            ))}
                        </div>
                    ) : (
                        <div className="flex h-full items-center justify-center text-[13px] text-[#6B7280]">
                            Start a conversation by typing a message below.
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <ChatInput 
                    value={inputMessage}
                    onChange={setInputMessage}
                    onSubmit={handleSendMessage}
                    placeholder="Ask a question..."
                />
            </main>
        </div>
    );
}