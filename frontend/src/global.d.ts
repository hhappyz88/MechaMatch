declare module '*.svelte' {
  import type { SvelteComponentTyped } from 'svelte';

  // You can specify empty props/events/slots or keep them generic like this:
  export default class SvelteComponent extends SvelteComponentTyped<
    Record<string, unknown>, // props
    Record<string, unknown>, // events
    Record<string, unknown> // slots
  > {}
}
