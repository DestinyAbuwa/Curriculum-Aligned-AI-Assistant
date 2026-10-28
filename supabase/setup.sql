-- UICOMP Curriculum AI Assistant: database setup for saved chats.
-- Paste this into Supabase Dashboard -> SQL Editor and click Run.
-- Safe to run more than once: it won't recreate tables that already exist.

-- 1. Tables the app uses -------------------------------------------------------

-- One row per chat.
create table if not exists public.threads (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null default auth.uid() references auth.users (id) on delete cascade,
  title      text not null default 'New Chat',
  preview    text,
  created_at timestamptz not null default now()
);

-- One row per message inside a chat.
create table if not exists public.messages (
  id         uuid primary key default gen_random_uuid(),
  thread_id  uuid not null references public.threads (id) on delete cascade,
  sender     text not null check (sender in ('user', 'assistant')),
  author     text,
  content    text not null,
  created_at timestamptz not null default now()
);

-- 2. Privacy rules: each signed-in user only sees and changes their own chats ----

alter table public.threads  enable row level security;
alter table public.messages enable row level security;

drop policy if exists "Users manage their own threads" on public.threads;
create policy "Users manage their own threads" on public.threads
  for all to authenticated
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

drop policy if exists "Users manage messages in their own threads" on public.messages;
create policy "Users manage messages in their own threads" on public.messages
  for all to authenticated
  using (exists (
    select 1 from public.threads
    where threads.id = messages.thread_id and threads.user_id = auth.uid()
  ))
  with check (exists (
    select 1 from public.threads
    where threads.id = messages.thread_id and threads.user_id = auth.uid()
  ));
