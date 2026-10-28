import React from 'react';

/*
  Shown instead of the app when the Supabase keys are missing from .env.local.
  Without them Supabase can't start, and the page would otherwise stay blank.
  main.jsx decides whether to show this or the real app.
*/
export function MissingKeysNotice() {
    return (
        <div className="flex h-screen w-full items-center justify-center bg-white px-6">
            <div className="w-full max-w-[520px] rounded-2xl p-8 ring-1 ring-inset ring-[#E5E7EB]">
                <h1 className="text-2xl font-bold leading-[31px] text-[#13294B]">Supabase keys missing</h1>
                <p className="mt-2 text-sm leading-5 text-[#6B7280]">
                    The app can't start until it knows which Supabase project to use.
                </p>

                <ol className="mt-6 list-decimal space-y-3 pl-5 text-sm leading-5 text-[#111827]">
                    <li>
                        In the project folder (next to <code className="font-mono text-[13px]">package.json</code>),
                        create a file named <code className="font-mono text-[13px]">.env.local</code> with:
                        <pre className="mt-2 overflow-x-auto rounded-xl bg-[#F4F4F6] p-4 font-mono text-[13px] leading-5 text-[#13294B]">
{`VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key`}
                        </pre>
                        <p className="mt-2 text-[#6B7280]">
                            Both values are in the Supabase Dashboard under Project Settings → API.
                        </p>
                    </li>
                    <li>
                        Stop the server (<code className="font-mono text-[13px]">Ctrl + C</code>) and run{' '}
                        <code className="font-mono text-[13px]">npm run dev</code> again.
                    </li>
                </ol>
            </div>
        </div>
    );
}
