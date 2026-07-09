-- Growth Book tracker — run this ONCE in your Supabase SQL Editor
-- (statract.com project → SQL Editor → New query → paste → Run).
-- Creates the transactions table and locks it down so ONLY the logged-in
-- owner can ever see or change their own rows (Row-Level Security).

create table if not exists public.gb_transactions (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null default auth.uid() references auth.users(id) on delete cascade,
  account    text not null check (account in ('schwab','etrade')),
  date       date not null,
  type       text not null check (type in ('deposit','withdraw','buy','sell','mark')),
  shares     numeric,
  price      numeric,
  amount     numeric,
  created_at timestamptz not null default now()
);

create index if not exists gb_transactions_user_idx on public.gb_transactions (user_id, date);

alter table public.gb_transactions enable row level security;

-- Each policy restricts access to rows the signed-in user owns.
drop policy if exists gb_sel on public.gb_transactions;
drop policy if exists gb_ins on public.gb_transactions;
drop policy if exists gb_del on public.gb_transactions;
drop policy if exists gb_upd on public.gb_transactions;

create policy gb_sel on public.gb_transactions for select using (auth.uid() = user_id);
create policy gb_ins on public.gb_transactions for insert with check (auth.uid() = user_id);
create policy gb_del on public.gb_transactions for delete using (auth.uid() = user_id);
create policy gb_upd on public.gb_transactions for update using (auth.uid() = user_id);

-- Logged-in users need table privileges too (RLS above then limits them to their OWN rows).
-- 'anon' (not signed in) is deliberately granted nothing.
grant select, insert, update, delete on public.gb_transactions to authenticated;
