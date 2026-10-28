import React, { useState, useEffect } from 'react';
import { Lock, Eye, EyeOff, User } from 'lucide-react';
import { supabase } from '../supabaseClient';
import uicLogo from '../assets/uic-logo-figma.png';
import mailIcon from '../assets/icons/mail.svg';

const inputClass = 'min-w-0 flex-1 bg-transparent text-sm leading-5 text-[#111827] outline-none placeholder:text-[#6B7280]';
const iconClass = 'shrink-0 text-[#6B7280]';

function Field({ label, icon, hint, children }) {
    return (
        <label className="flex flex-col gap-1.5">
            <span className="text-[13px] font-medium leading-4 text-[#13294B]">{label}</span>
            <span className="flex h-[52px] items-center gap-3 rounded-full bg-[#F4F4F6] pl-[18px] pr-3.5 focus-within:ring-2 focus-within:ring-[#13294B]/20">
                {icon}
                {children}
            </span>
            {hint && <span className="px-[18px] text-xs leading-4 text-[#6B7280]">{hint}</span>}
        </label>
    );
}

export function AuthPage({ onLoginSuccess }) {
    const [authMode, setAuthMode] = useState('login'); // 'login' or 'signup'
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const [fullName, setFullName] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    const [errorMessage, setErrorMessage] = useState('');
    const [infoMessage, setInfoMessage] = useState('');

    useEffect(() => {
        setErrorMessage('');
        setInfoMessage('');
    }, [authMode]);

    // Translate automated Supabase errors into natural human messages
    const getHumanReadableError = (errorMsg, mode) => {
        const lowerMsg = errorMsg.toLowerCase();
        
        if (lowerMsg.includes('invalid login credentials')) {
            return mode === 'login' 
                ? 'Incorrect email or password. Please double-check your credentials and try again.'
                : 'Invalid details provided.';
        }
        if (lowerMsg.includes('user already registered') || lowerMsg.includes('already exists')) {
            return 'An account with this UIC email already exists. Try logging in instead.';
        }
        if (lowerMsg.includes('email not confirmed')) {
            return 'Please check your UIC email inbox and confirm your email address before logging in.';
        }
        if (lowerMsg.includes('password should be at least')) {
            return 'Password must be at least 8 characters long.';
        }

        return errorMsg;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const trimmedEmail = email.trim().toLowerCase();

        if (!trimmedEmail || !password.trim()) return;
        setErrorMessage('');
        setInfoMessage('');

        // 1. Email format check
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(trimmedEmail)) {
            setErrorMessage('Please enter a valid email address.');
            return;
        }

        // 2. Strict @uic.edu check
        if (!trimmedEmail.endsWith('@uic.edu')) {
            setErrorMessage('Only official @uic.edu email addresses are allowed.');
            return;
        }

        // Handle Log In
        if (authMode === 'login') {
            const { data, error } = await supabase.auth.signInWithPassword({ email: trimmedEmail, password });
            if (error) {
                setErrorMessage(getHumanReadableError(error.message, 'login'));
                return;
            }
            onLoginSuccess(data.user);
            return;
        }

        // Handle Sign Up
        if (password.length < 8) {
            setErrorMessage('Password must be at least 8 characters.');
            return;
        }
        if (password !== confirmPassword) {
            setErrorMessage('Passwords do not match.');
            return;
        }

        const { data, error } = await supabase.auth.signUp({
            email: trimmedEmail,
            password,
            options: { data: { full_name: fullName.trim() } },
        });

        if (error) {
            setErrorMessage(getHumanReadableError(error.message, 'signup'));
            return;
        }

        if (!data.session) {
            setInfoMessage('Account created! Please check your UIC inbox to confirm your email before logging in.');
            return;
        }
        onLoginSuccess(data.user);
    };

    const isLogin = authMode === 'login';

    const passwordToggle = (
        <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
            className="shrink-0 cursor-pointer text-[#6B7280] transition-colors hover:text-[#13294B]"
        >
            {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
        </button>
    );

    return (
        <div className="flex h-screen w-full overflow-hidden bg-white">
            {/* Left side panel */}
            <div className="hidden w-[480px] shrink-0 flex-col items-start justify-center gap-5 bg-[#13294B] px-14 pb-14 pt-16 md:flex">
                <img src={uicLogo} alt="UIC" className="h-16 w-16 rounded-[20px] object-cover" />
                <h1 className="text-[28px] font-bold leading-9 text-white">
                    UICOMP Curriculum AI Assistant
                </h1>
                <div className="h-1 w-12 rounded-[2px] bg-[#D41F34]" />
                <p className="text-[15px] leading-6 text-white/80">
                    Official UICOMP Internal Medical Education Assistant. Answers are generated strictly from verified course materials.
                </p>
            </div>

            {/* Right side form */}
            <div className="flex min-w-0 flex-1 flex-col items-center overflow-y-auto px-6 pb-12 pt-[120px]">
                <div className="flex w-full max-w-[400px] flex-col gap-5">

                    {/* Mode selector */}
                    <div className="flex gap-1 rounded-full bg-[#F4F4F6] p-1">
                        <button
                            type="button"
                            onClick={() => setAuthMode('login')}
                            className={`h-10 flex-1 cursor-pointer rounded-full text-sm font-medium leading-5 transition-colors ${
                                isLogin ? 'bg-[#13294B] text-white' : 'text-[#6B7280] hover:text-[#13294B]'
                            }`}
                        >
                            Log In
                        </button>
                        <button
                            type="button"
                            onClick={() => setAuthMode('signup')}
                            className={`h-10 flex-1 cursor-pointer rounded-full text-sm font-medium leading-5 transition-colors ${
                                !isLogin ? 'bg-[#13294B] text-white' : 'text-[#6B7280] hover:text-[#13294B]'
                            }`}
                        >
                            Sign Up
                        </button>
                    </div>

                    {/* Title section */}
                    <div className="flex flex-col gap-2">
                        <h2 className="text-2xl font-bold leading-[31px] text-[#13294B]">
                            {isLogin ? 'Log in' : 'Create your account'}
                        </h2>
                        <p className="text-sm leading-5 text-[#6B7280]">
                            {isLogin
                                ? 'Access the UICOMP Curriculum AI Assistant.'
                                : 'Use your UIC email to get started.'}
                        </p>
                    </div>

                    {/* Input form */}
                    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
                        <div className="flex flex-col gap-4">

                            {!isLogin && (
                                <Field label="Full name" icon={<User size={20} className={iconClass} />}>
                                    <input
                                        type="text"
                                        value={fullName}
                                        onChange={(e) => setFullName(e.target.value)}
                                        placeholder="Enter your full name"
                                        className={inputClass}
                                    />
                                </Field>
                            )}

                            <Field
                                label="UIC Email"
                                icon={<img src={mailIcon} alt="" className="shrink-0" />}
                            >
                                <input
                                    type="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="netid@uic.edu"
                                    className={inputClass}
                                />
                            </Field>

                            <Field
                                label="Password"
                                icon={<Lock size={20} className={iconClass} />}
                                hint={isLogin ? null : 'At least 8 characters.'}
                            >
                                <input
                                    type={showPassword ? "text" : "password"}
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder={isLogin ? 'Enter your password' : 'Create a password'}
                                    className={inputClass}
                                />
                                {passwordToggle}
                            </Field>

                            {!isLogin && (
                                <Field label="Confirm password" icon={<Lock size={20} className={iconClass} />}>
                                    <input
                                        type={showPassword ? "text" : "password"}
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        placeholder="Re-enter your password"
                                        className={inputClass}
                                    />
                                    {passwordToggle}
                                </Field>
                            )}

                            {isLogin && (
                                <div className="flex justify-end">
                                    <a href="#forgot" className="rounded-lg px-1 py-0.5 text-sm font-medium leading-5 text-[#2563EB] hover:underline">
                                        Forgot password?
                                    </a>
                                </div>
                            )}
                        </div>

                        {errorMessage && <p className="text-sm leading-5 text-[#D41F34]">{errorMessage}</p>}
                        {infoMessage && <p className="text-sm leading-5 text-[#13294B]">{infoMessage}</p>}

                        <button
                            type="submit"
                            className="h-12 w-full cursor-pointer rounded-xl bg-[#D41F34] text-[15px] font-semibold leading-5 text-white transition-colors hover:bg-[#BC1A2D]"
                        >
                            {isLogin ? 'Log In' : 'Sign Up'}
                        </button>
                    </form>

                    <p className="flex items-center justify-center gap-1 text-sm leading-5 text-[#6B7280]">
                        {isLogin ? (
                            <>
                                Don’t have an account?
                                <button
                                    type="button"
                                    onClick={() => setAuthMode('signup')}
                                    className="cursor-pointer rounded-lg px-1 py-0.5 font-medium text-[#2563EB] hover:underline"
                                >
                                    Sign up
                                </button>
                            </>
                        ) : (
                            <>
                                Already have an account?
                                <button
                                    type="button"
                                    onClick={() => setAuthMode('login')}
                                    className="cursor-pointer rounded-lg px-1 py-0.5 font-medium text-[#2563EB] hover:underline"
                                >
                                    Log in
                                </button>
                            </>
                        )}
                    </p>
                </div>
            </div>
        </div>
    );
}