#include<iostream>
#include <bits/stdc++.h>

#define ll long long
#define ld  long double

#define IO ios_base::sync_with_stdio(0); cin.tie(0); cout.tie(0);
using namespace std;
const int N = 2000 + 5, MOD = 998244353;
random_device rd;
mt19937_64 rng(rd());

string get_str(int len) {
    string s = "\\/_";
    string ans = "";
    while (ans.size() < len) {
        ll idx = rng() % 3;
        ans += (char) (rng() % 3) + 'a';
        ans.back() = s[idx];
    }
    return ans;
}

void prnt_vector(vector<int> &a) {
    for (int i = 0; i < a.size(); i++) {
        cout << a[i];
        if (i != a.size() - 1) cout << " ";
    }
    cout << endl;
}

void prnt_vector(vector<ll> a) {
    for (int i = 0; i < a.size(); i++) {
        cout << a[i];
        if (i != a.size() - 1) cout << " ";
    }
    cout << endl;
}

vector<ll> gen_vector(int n, ll l, ll r) {
    vector<ll> a(n);
    uniform_int_distribution<ll> dis(l, r);
    for (int i = 0; i < n; i++) {
        a[i] = dis(rng);
    }
    return a;
}

void gen() {
    freopen("input.txt", "w", stdout);
    int t = 1;
    const ll mx_n = 1800;
    const ll mx_q = 1e4;
    const ll aaaa = 1e8;
    while (t--) {
        ll n = 1999;
        cout << n << endl;
        vector<ll> order(2 * n);
        iota(order.begin(), order.end(), 1);
        shuffle(order.begin(), order.end(), rng);
        for (int i = 1; i < order.size(); i++) {
            uniform_int_distribution<ll> dis(max(0 , i - 2), i - 1);
            int u = order[i];
            int v = order[dis(rng)];
            cout << u << " " << v << endl;
        }
    }
}

vector<int> adj[2 * N];
int sz[2 * N];
int dp[2 * N][N][2];

void add(int &x, int y) {
    x = (x + 1ll * y) % MOD;
}

void merge(int x, int y) {
    vector<vector<int> > ans(2, vector<int>((sz[x] + sz[y]) / 2 + 2, 0));
    for (int i = 0; i <= sz[x] / 2; i++) {
        for (int j = 0; j <= sz[y] / 2; j++) {
            int dp00 = 1ll * dp[x][i][0] * dp[y][j][0] % MOD;
            int dp01 = 1ll * dp[x][i][0] * dp[y][j][1] % MOD;
            int dp10 = 1ll * dp[x][i][1] * dp[y][j][0] % MOD;
            int dp11 = 1ll * dp[x][i][1] * dp[y][j][1] % MOD;


            add(ans[0][i + j], dp00 + dp01);
            add(ans[1][i + j], dp10 + dp11); // 1 0
            add(ans[1][i + j + 1], dp00);
        }
    }
    for (int i = 0; i < ans[0].size(); i++) {
        dp[x][i][0] = ans[0][i];
        dp[x][i][1] = ans[1][i];
    }
}

void solve(int node, int par) {
    sz[node] = 1;
    dp[node][0][0] = 1;

    for (auto child: adj[node]) {
        if (child == par)continue;
        solve(child, node);
        merge(node, child);
        sz[node] += sz[child];
    }
}

void doWork() {
    int n;
    cin >> n;
    for (int i = 1; i < 2 * n; i++) {
        int x, y;
        cin >> x >> y;
        adj[x].push_back(y);
        adj[y].push_back(x);
    }
    solve(1, 0);
    ll p = 1;
    ll ans = 0;
    int f = 0;
    for (int i = n; i >= 0; i--) {
        ll cnt = dp[1][i][0] + dp[1][i][1];
        if (i % 2)cnt = -cnt;
        ans += cnt * p;
        ans %= MOD;
        f += 2;
        p = p * (f - 1) % MOD;
    }
    ans = (ans + MOD) % MOD;
    cout << ans;
}

int main() {
    IO
    // gen();
    // return 0;
    // freopen("input.txt", "r", stdin);
    // freopen("output.txt", "w", stdout);
    int t = 1;
    // cin >> t;
    for (int i = 1; i <= t; i++) {
        // cout << "Case #" << i << ": ";
        doWork();
    }
}
