import React from 'react';
import { PanelLeftOpen } from 'lucide-react';

/*
  Title bar at the top of the chat screen: logo, title and subtitle, centered.
  When the sidebar is closed, a button at the top left opens it again.
*/
export function Header({ isSidebarOpen, onOpenSidebar, title, subtitle }) {
    // The first word ("UICOMP") is shown in red and the rest in navy, as in the Figma.
    const [firstWord, ...otherWords] = title.split(' ');

    return (
        <header className="relative flex shrink-0 flex-col items-center">
            {!isSidebarOpen && (
                <button
                    type="button"
                    onClick={onOpenSidebar}
                    aria-label="Open sidebar"
                    title="Open sidebar"
                    className="absolute left-0 top-0 flex h-9 w-9 cursor-pointer items-center justify-center rounded-lg text-[#13294B] transition-colors hover:bg-[#F4F4F6]"
                >
                    <PanelLeftOpen size={20} />
                </button>
            )}
            <div className="flex items-center gap-2.5">
                <img src="/uic-logo.png" alt="UIC" className="h-9 w-9 shrink-0 rounded-full object-cover" />
                <h1 className="text-2xl font-semibold leading-[31px] text-[#13294B]">
                    <span className="text-[#D41F34]">{firstWord}</span> {otherWords.join(' ')}
                </h1>
            </div>
            {subtitle && (
                <p className="mt-2 text-center text-[13px] leading-[19px] text-[#6B7280]">{subtitle}</p>
            )}
        </header>
    );
}
