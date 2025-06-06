<script lang="ts">
  import SessionCard from './SessionCard.svelte';
  import type { Session } from '$lib';

  export let sessions: Session[];
</script>

<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
  {#each sessions as session (session.id)}
    <SessionCard {session} />
  {/each}
</div>
