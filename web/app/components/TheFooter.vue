<script setup lang="ts">
import { APIFY_URL, AUTHOR_URL, GITHUB_URL } from "~/content/data"
import type { Copy } from "~/content/types"

defineProps<{ copy: Copy }>()
</script>

<template>
  <footer class="footer wrap">
    <hr class="rule-double" />
    <div class="footer__grid">
      <div class="footer__legal">
        <p>{{ copy.footer.attribution }}</p>
        <p>{{ copy.footer.noAffiliation }}</p>
        <p>{{ copy.footer.disclaimer }}</p>
      </div>
      <p class="footer__sign">
        {{ copy.footer.madeBy }} <a :href="AUTHOR_URL">VazquezDev</a>
      </p>
      <ul class="footer__links">
        <li><a :href="APIFY_URL">Apify Store</a></li>
        <li><a :href="GITHUB_URL">{{ copy.footer.source }}</a></li>
        <li>{{ copy.footer.license }}</li>
      </ul>
    </div>
    <p class="footer__colophon">{{ copy.footer.colophon }}</p>
  </footer>
</template>

<style scoped>
.footer {
  padding-bottom: var(--space-m);
  color: var(--ink-faded);
  font-size: var(--step--1);
}

.footer__grid {
  display: grid;
  gap: var(--space-s) var(--gap);
  padding-top: var(--space-s);
}

.footer__legal {
  display: grid;
  gap: 0.4rem;
  max-width: 52ch;
}

.footer__sign {
  color: var(--ink);
  font-size: var(--step-0);
}

.footer__links {
  display: grid;
  gap: 0.4rem;
  padding: 0;
  list-style: none;
}

.footer__colophon {
  margin-top: var(--space-m);
  font-style: italic;
}

@media (min-width: 1024px) {
  .footer__grid {
    grid-template-columns: repeat(12, minmax(0, 1fr));
  }

  .footer__legal {
    grid-column: 1 / span 6;
  }

  .footer__sign {
    grid-column: 8 / span 2;
  }

  .footer__links {
    grid-column: 10 / span 3;
  }
}
</style>
