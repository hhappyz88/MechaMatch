<script lang="ts">
  import { statusColours, type Session } from '$lib';

  export let session: Session;
</script>

<div class="space-y-2 rounded-xl border p-4 shadow-sm">
  <div class="flex items-center justify-between">
    <h3 class="text-lg font-semibold">{session.name}</h3>
    <span class={`rounded px-2 py-1 text-sm font-medium ${statusColours[session.status]}`}>
      {session.status}
    </span>
  </div>
  <p class="text-sm text-gray-500">Last run: {session.lastRun}</p>
</div>
