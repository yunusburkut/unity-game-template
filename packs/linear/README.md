# linear

Oyunun işlerini Linear'da takip ediyorsan. `linear-scout` agent'ı bir iş için açık ya da kapanmış issue'yu bulur,
kararlarını okur ve uzun issue listelerini ana konuşmaya taşımaz. Sadece okur.

## Kurulum

1. Claude'da **Linear MCP bağlı olmalı**. Agent'ın `tools:` satırındaki `mcp__49619aea-...` kimliği senin şu anki Linear
   bağlantın; bağlantıyı yeniden kurarsan, başka hesapta ya da makinede kimlik değişebilir, o satırı güncelle.
   Kontrol: oyunun oturumunda Claude'a "Linear `list_issues` aracının tam adı ne?" diye sor; `mcp__<kimlik>__list_issues`
   içindeki kimlik `tools:` satırındakiyle aynı olmalı. Kimlik eskiyse agent "Linear araçları yok" der ve durur.
2. `.claude/agents/linear-scout.md` içinde `__TEAM__` yerine takım anahtarını yaz (ör. `MIX`) ve TODO satırını
   toplayıcı issue'larınla doldur.
3. Aşağıdaki parçayı CLAUDE.md'nin **Working agreement** bölümüne ekle.

```markdown
Every change belongs to a Linear __TEAM__ issue. Before development, scene, asset or settings work, ask `linear-scout`
which issue covers it; if none does, propose a new one under the collector it names and wait for my OK before
creating it. Mention the issue number in the commit message.
```
