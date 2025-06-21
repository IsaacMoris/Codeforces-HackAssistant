#include <bits/stdc++.h>
using namespace std;

using vii = vector<pair<int, int>>;
using vll = vector<pair<long long, long long>>;
using vi  = vector<int>;
using vl  = vector<long long>;
using pii = pair<int, int>;
using pll = pair<long long, long long>;
using pil = vector<int, long long>;
using ll  = long long;
using ull = unsigned long long;

#define f first
#define s second 
#define pb push_back
#define endl '\n'
#define front_zero(n) __builtin_clzll(n)
#define back_zero(n) __builtin_ctzll(n)
#define total_one(n) __builtin_popcount(n)
#define all(x) x.begin(), x.end()
#define sz(x) (int)x.size()
#define loop1(n) for(int i = 1; i <= n; ++i)
#define loop0(n) for(int i = 0; i < n; ++i)
#define fastIO cin.tie(0)->sync_with_stdio(0)
mt19937 rng((unsigned int) chrono::steady_clock::now().time_since_epoch().count());


// #define LOCAL

#ifdef LOCAL
#include "algo/debug.h"
#else
#define deb(...) 42
#endif

// #include <ext/pb_ds/assoc_container.hpp>
// using namespace __gnu_pbds;

// template <typename T>
// using order_set = tree<T, null_type, less<T>, rb_tree_tag, tree_order_statistics_node_update>;
// order_of_key() *find_by_order()


const int maxn = 2e5 + 9;
int a[101][101];
int dx[] = {0, 0, -1, 1};
int dy[] = {-1, 1, 0, 0};
int n, m;
pair<int, int> tar = {-1, -1};
map<int, bool> mp[101];
bool check(int x, int y, int ch){
   if(mp[x][y])return false;
   if(a[x][y] == ch){
      if(x == tar.f && y == tar.s)return true;
      a[x][y] ^= 1;
      mp[x][y] = true;
      bool ok = false;
      for(int i = 0; i < 4; ++i){
         int xx = x + dx[i];
         int yy = y + dy[i];
         if(xx >= 1 && xx <= n && yy >= 1 && yy <= m){
            ok |= check(xx, yy, ch);
         }
      }
      return ok;
   }
   return false;
   

}


void solve(){
   cin >> n >> m;
   for(int i = 1; i <= n; ++i){
      for(int j = 1; j <= m; ++j){
         cin >> a[i][j];
      }
   }
   int x1, y1, x2, y2;
   cin >> x1 >> y1 >> x2 >> y2;
   int f = 1;
   while(true){
      for(int i = 1; i <= n; ++i){
         mp[i].clear();
      }
      if(f){
         tar = {x2, y2};
      }
      else {
         tar = {x1, y1};
      }
      if(f && check(x1, y1, a[x1][y1])){
         cout << "Kaiji" << endl;
         return;
      }
      else if(!f && check(x2, y2, a[x2][y2])){
         cout << "Chairman" << endl;
         return;
      }
      // for(int i = 1; i <= n; ++i){
      //    for(int j = 1; j <= m; ++j){
      //       cout << a[i][j] << ' ';
      //    }
      //    cout << endl;
      // }
      // cout << endl;
      f ^= 1;
   }

}

int main(){
    fastIO;
    int tt = 1;
    cin >> tt;
    while(tt--){
     solve();
    }

}