<script lang="ts">
  import SessionList from '$lib/components/SessionList.svelte';
  import type { Session } from '$lib';

  const sessions: Session[] = [
    {
      id: '1',
      name: 'First Session',
      status: 'completed',
      lastRun: '2025-06-01 14:30'
    },
    {
      id: '2',
      name: 'Second Session',
      status: 'running',
      lastRun: '2025-06-02 09:12'
    },
    {
      id: '3',
      name: 'Third Session',
      status: 'pending',
      lastRun: '2025-06-03 17:45'
    },
    {
      id: '4',
      name: 'Failed Session',
      status: 'failed',
      lastRun: '2025-06-03 18:00'
    }
  ];
</script>

<main class="p-6 space-y-6">
  <h1 class="text-2xl font-bold">Sessions</h1>
  <SessionList {sessions} />
</main>
