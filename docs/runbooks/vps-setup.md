# Runbook — VPS and domain setup for lifeofai.adnered.net

Server: mikr.us VPS (2 GB RAM), nginx already running behind Cloudflare. The site is **static files only**.

Legend: **[HUMAN]** done by the owner (root on the VPS, Cloudflare, GitHub settings) · **[AGENT]** the implementing agent may prepare this in the repo, but **never connects to the VPS**.

Placeholders used below: `<SSH_PORT>` (the VPS SSH port), `<VPS_HOST>` (hostname or IP used for SSH).

## 1. DNS

**[HUMAN]** In Cloudflare, add a record `lifeofai` for `adnered.net` the same way as the existing subdomains (same type/target, **proxied**).

Check: `dig +short lifeofai.adnered.net` returns Cloudflare addresses.

## 2. Web root and a restricted deploy user

**[HUMAN]** as root on the VPS:

```bash
# A user that can do nothing but receive files into the web root
adduser --disabled-password --gecos "" deploy-lifeofai
mkdir -p /var/www/lifeofai
chown deploy-lifeofai:www-data /var/www/lifeofai
chmod 755 /var/www/lifeofai

# rrsync restricts SSH to rsync into one directory
ls /usr/bin/rrsync || ls /usr/share/doc/rsync/scripts/rrsync*
# If only the .gz exists in the docs folder:
#   gunzip -c /usr/share/doc/rsync/scripts/rrsync.gz > /usr/local/bin/rrsync && chmod 755 /usr/local/bin/rrsync
```

## 3. Deploy key

**[HUMAN]** on the Mac (not on the VPS):

```bash
ssh-keygen -t ed25519 -f ~/.ssh/lifeofai_deploy -N "" -C "github-actions lifeofai deploy"
cat ~/.ssh/lifeofai_deploy.pub
```

**[HUMAN]** on the VPS, as root. One line, using the path to rrsync found in step 2:

```bash
mkdir -p /home/deploy-lifeofai/.ssh
echo 'command="/usr/bin/rrsync /var/www/lifeofai",restrict ssh-ed25519 AAAA...(public key)... github-actions lifeofai deploy' \
  > /home/deploy-lifeofai/.ssh/authorized_keys
chown -R deploy-lifeofai:deploy-lifeofai /home/deploy-lifeofai/.ssh
chmod 700 /home/deploy-lifeofai/.ssh
chmod 600 /home/deploy-lifeofai/.ssh/authorized_keys
```

`restrict` disables shells, port forwarding and PTYs; `rrsync` only allows rsync inside `/var/www/lifeofai`. If the key ever leaks, the worst case is someone overwriting the static site, which the next deploy restores.

Check from the Mac (should list nothing or the site files, and must **not** give a shell):

```bash
rsync -e "ssh -i ~/.ssh/lifeofai_deploy -p <SSH_PORT>" deploy-lifeofai@<VPS_HOST>:./
ssh -i ~/.ssh/lifeofai_deploy -p <SSH_PORT> deploy-lifeofai@<VPS_HOST>    # expected: refused / rrsync error
```

## 4. nginx

**[AGENT]** keeps the template in `deploy/nginx/lifeofai.adnered.net.conf`.

**[HUMAN]** as root:

```bash
# Compare listen/ssl lines with an existing working site first:
ls /etc/nginx/sites-enabled/
cat /etc/nginx/sites-enabled/<existing-site>

cp lifeofai.adnered.net.conf /etc/nginx/sites-available/
# edit <SSL_CERT>/<SSL_KEY> (and listen lines if the existing site differs)
ln -s /etc/nginx/sites-available/lifeofai.adnered.net.conf /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

Certificate: whatever the existing sites use, either `certbot --nginx -d lifeofai.adnered.net` or a Cloudflare Origin Certificate. With an Origin Certificate, set the Cloudflare SSL mode to *Full (strict)*.

Temporary check before the first deploy:

```bash
echo '<h1>life-of-ai: coming soon</h1>' > /var/www/lifeofai/index.html
chown deploy-lifeofai:www-data /var/www/lifeofai/index.html
curl -sI https://lifeofai.adnered.net | head -n 20     # 200 + the security headers
```

## 5. GitHub secrets

**[HUMAN]** in the repo: *Settings → Secrets and variables → Actions → New repository secret*:

| Secret | Value |
|---|---|
| `VPS_HOST` | `<VPS_HOST>` |
| `VPS_PORT` | `<SSH_PORT>` |
| `VPS_USER` | `deploy-lifeofai` |
| `VPS_SSH_KEY` | full contents of `~/.ssh/lifeofai_deploy` (the private key) |
| `VPS_KNOWN_HOSTS` | output of `ssh-keyscan -p <SSH_PORT> <VPS_HOST>` |

Optional but recommended: *Settings → Environments → production → Deployment branches: main only*.

The agent's token has no permission to read or change secrets; keep it that way.

## 6. First deploy

**[AGENT]** after milestone W1 is merged, the `Deploy web` workflow runs on push to `main`, or manually via *Actions → Deploy web → Run workflow*.

**[HUMAN]** checks `https://lifeofai.adnered.net` shows the viewer and "Load sample" works.

## Resource check

Static files through the existing nginx add only a few MB of RAM. The VPS currently uses ~20% of 2 GB, so this adds nothing meaningful.
