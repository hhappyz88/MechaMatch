<script lang="ts">
  import { statusColours , type Session } from '$lib';

  export let session: Session;
</script>

<div class="rounded-xl border p-4 shadow-sm space-y-2">
  <div class="flex justify-between items-center">
    <h3 class="text-lg font-semibold">{session.name}</h3>
    <span class={`font-medium px-2 py-1 text-sm rounded ${statusColours[session.status]}`}>
      {session.status}
    </span>
  </div>
  <p class="text-sm text-gray-500">Last run: {session.lastRun}</p>
</div>
