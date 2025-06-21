/*
Author : MNnazrul
Date   : 2023-06-17 12:15:20
*/

#include<bits/stdc++.h>
using namespace std;
 
// #include <ext/pb_ds/assoc_container.hpp>
// #include<ext/pb_ds/tree_policy.hpp>
// using namespace __gnu_pbds;
// using namespace __gnu_cxx;
// template <typename T> using oset = tree<T, null_type, less<T>, rb_tree_tag, tree_order_statistics_node_update>;
 
// #define int long long
#define endl "\n"
#define vi vector<int>
#define pb push_back
#define size(a) (int)a.size()
#define all(v) v.begin(), v.end()
#define rall(v) v.rbegin(), v.rend()
#define bp(x) __builtin_popcountll(x)
int const N = 2e5 + 5, mod = 1e9 + 7;

int ax[] = {1, -1, 0, 0};
int ay[] = {0, 0, 1, -1};
int cs = 1;
 
void solve() {
    int n, m; cin >> n >> m;

    bool ar[n + 3][m + 4];
    bool clr[n + 3][m + 4];
    int vis[n + 3][m + 4];
    memset(ar, 0, sizeof ar);
    memset(clr, 0, sizeof clr);
    memset(vis, 0, sizeof vis);
    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= m; j++) cin >> ar[i][j];
    }
    int x1, y1, x0, y0;
    cin >> x1 >> y1 >> x0 >> y0;

    vis[x1][y1] = 1;
    vis[x0][y0] = 2;
    
    bool f = true;


    auto valid = [&] (int x, int y) {
        if(x >= 1 and x <= n and y >=1 and y <= m) return true;
        return false;
    };

    while(1) {
        memset(clr, 0, sizeof clr);
        queue<pair<int, int>> q;

        if(f) {
            int p1 = ar[x1][y1];
            q.push({x1, y1});
            while(!q.empty()) {
                auto[x, y] = q.front();
                q.pop();

                vis[x][y] = 1;
                clr[x][y] = 1;
                ar[x][y] ^= 1;
                // cout << x << '/*/**/*/ ' << y << ' ' << p1 << endl;

                for (int i = 0; i < 4; i++) {
                    int x2 = x + ax[i], y2 = ay[i] + y;
                    if(valid(x2, y2) and !clr[x2][y2] and ar[x2][y2] == p1) {
                        if(vis[x2][y2] == 2) {
                            cout << "Kaiji" << endl;
                            return;
                        }
                        if(vis[x2][y2] == 0 or vis[x2][y2] == 1) q.push({x2, y2});
                        clr[x2][y2] = 1;
                    }
                }

            }

            // for (int i = 1; i <= n; i++) {
            //     for (int j = 1; j <= m; j++) cout << ar[i][j] << ' '; 
            //         cout << endl;
            // }
            // cout << endl;
            // // if(cs == 2) break;
            // cs++;

        }
        else {
            int p1 = ar[x0][y0];
            q.push({x0, y0});
            while(!q.empty()) {
                auto[x, y] = q.front();
                q.pop();

                vis[x][y] = 2;
                clr[x][y] = 1;
                ar[x][y] ^= 1;
                // cout << x << '/*/**/*/ ' << y << ' ' << p1 << endl;

                for (int i = 0; i < 4; i++) {
                    int x2 = x + ax[i], y2 = ay[i] + y;
                    if(valid(x2, y2) and !clr[x2][y2] and ar[x2][y2] == p1) {
                        if(vis[x2][y2] == 1) {
                            cout << "Chairman" << endl;
                            return;
                        }
                        if(vis[x2][y2] == 0 or vis[x2][y2] == 2) q.push({x2, y2});
                        clr[x2][y2] = 1;
                    }
                }

            }



        }


        f ^= 1;
    }


}
 
int32_t main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    int TestCase = 1;
    cin >> TestCase;  
    while(TestCase--)
        solve();
    return 0;
}