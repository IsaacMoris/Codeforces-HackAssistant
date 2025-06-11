#include "bits/stdc++.h"

#define int long long
#define all(x) x.begin(), x.end()

const int mod = 998244353;

int qmi(int a, int k) {
    int ans = 1;
    while (k) {
        if (k & 1) ans = ans * a % mod;
        k >>= 1;
        a = a * a % mod;
    }
    return ans % mod;
}

constexpr int N = 4e3 + 10;

int fact[N];
inline int mo(int x) {
    return (x % mod + mod) % mod;
}
int dp[N][N][2];
std::vector<int> G[N];
int sz[N];
void solve() {
    int n;
    std::cin >> n;
    for (int i = 0; i < 2 * n - 1; i++) {
        int u, v;
        std::cin >> u >> v;
        u --, v --;
        G[u].push_back(v);
        G[v].push_back(u);
    }
    auto dfs1 = [&](auto self, int u, int fa) -> void {
        sz[u] = 1;
        for (int v : G[u]) {
            if (v == fa) continue;
            self(self, v, u);
            sz[u] += sz[v];
        }
    };
    dfs1(dfs1, 0, -1);
    auto dfs = [&](auto self, int u, int fa) -> void {
        dp[u][0][0] = 1;
        for (int v : G[u]) {
            if (v == fa) continue;
            self(self, v, u);
            for (int i = sz[u] / 2; i >= 1; i--) {
                // for (int j = 0; j <= std::min(i, sz[v] / 2); j++) {
                //     if (j) dp[u][i][0] += dp[u][i - j][0] * (dp[v][j][0] + dp[v][j][1]);
                //     dp[u][i][0] = mo(dp[u][i][0]);
                //     if (j) dp[u][i][1] += dp[u][i - j][1] * (dp[v][j][0] + dp[v][j][1]);
                //     dp[u][i][1] = mo(dp[u][i][1]);
                //     if (i != j) dp[u][i][1] += dp[u][i - j - 1][0] * dp[v][j][0];
                //     dp[u][i][1] = mo(dp[u][i][1]);
                // }

                if (sz[v] < sz[u] - sz[v]) {
                    for (int j = 0; j <= sz[v] / 2; j++) {
                        if (j) dp[u][i][0] += dp[u][i - j][0] * (dp[v][j][0] + dp[v][j][1]);
                        dp[u][i][0] = mo(dp[u][i][0]);
                        if (j) dp[u][i][1] += dp[u][i - j][1] * (dp[v][j][0] + dp[v][j][1]);
                        dp[u][i][1] = mo(dp[u][i][1]);
                        if (i != j) dp[u][i][1] += dp[u][i - j - 1][0] * dp[v][j][0];
                        dp[u][i][1] = mo(dp[u][i][1]);
                    }
                } else {
                    for (int k = 0; k <= (sz[u] - sz[v]) / 2 + 1; k ++) {
                        int j = i - k;
                        if (j) dp[u][i][0] += dp[u][i - j][0] * (dp[v][j][0] + dp[v][j][1]);
                        dp[u][i][0] = mo(dp[u][i][0]);
                        if (j) dp[u][i][1] += dp[u][i - j][1] * (dp[v][j][0] + dp[v][j][1]);
                        dp[u][i][1] = mo(dp[u][i][1]);
                        if (i != j) dp[u][i][1] += dp[u][i - j - 1][0] * dp[v][j][0];
                        dp[u][i][1] = mo(dp[u][i][1]);
                    }
                }
            }
        }
    };
    dfs(dfs, 0, -1);
    auto f = [&](int x) {
        int y = x / 2;
        return fact[x] * qmi(qmi(2, y), mod - 2) % mod * qmi(fact[y], mod - 2) % mod;
    };
    int ans = f(2 * n);
    for (int i = 1; i <= n; i ++) {
        int cur = (dp[0][i][0] + dp[0][i][1]) % mod;
        cur = cur * f(2 * n - 2 * i) % mod;
        if (i & 1) ans -= cur;
        else ans += cur;
        ans = mo(ans);
    }
    std::cout << ans << "\n";
}

signed main() {
    std::ios::sync_with_stdio(false); std::cin.tie(0);
    fact[0] = 1;
    for (int i = 1; i < N; i ++) {
        fact[i] = fact[i - 1] * i % mod;
    }
    solve();
    return 0;
}