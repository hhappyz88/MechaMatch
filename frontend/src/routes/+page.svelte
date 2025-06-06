<script lang="ts">
  import { goto } from '$app/navigation';
</script>

<div class="flex min-h-screen flex-col items-center justify-center space-y-6 p-8">
  <h1 class="text-4xl font-bold">Scraper Dashboard</h1>

  <p class="text-lg text-gray-600">View, manage, and run your scraping sessions from here.</p>

  <button
    class="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white shadow hover:bg-blue-700"
    on:click={() => goto('/sessions')}
  >
    View Sessions
  </button>
</div>
