## 1. 概述

C++ 标准库中的 `std::string` 提供了比 C 风格字符串更安全、更方便的操作方式。位于头文件 `<string>` 中，属于 `std` 命名空间。它支持动态内存管理、自动拼接、丰富的查找替换接口以及与 STL 算法的良好兼容性。

---

## 2. 基本操作

### 2.1 声明与初始化

```cpp
#include <string>
using namespace std;

string s1;                 // 空串
string s2 = "hello";       // 拷贝初始化
string s3("world");        // 直接初始化
string s4(5, 'c');         // "ccccc"
string s5(s2);             // 拷贝构造
string s6(s2, 1, 3);       // 从下标1开始取3个字符 -> "ell"
```

### 2.2 输入输出

```cpp
string s;
cin >> s;                  // 读取到空白字符为止
getline(cin, s);           // 读取整行（包括空格）
cout << s;
```

### 2.3 拼接

```cpp
string a = "Hello";
string b = "World";
string c = a + " " + b;    // "Hello World"
a += "!";
```

### 2.4 比较

支持关系运算符 `==, !=, <, >, <=, >=`，按字典序比较。

```cpp
if (a == b) { /* ... */ }
if (a < "abc") { /* ... */ }
```

---

## 3. 常用成员方法

| 方法                       | 说明                                   | 示例                       |
| -------------------------- | -------------------------------------- | -------------------------- |
| `size()` / `length()`      | 返回字符串长度（字符数）               | `s.size()`                 |
| `empty()`                  | 是否为空                               | `s.empty()`                |
| `clear()`                  | 清空内容                               | `s.clear()`                |
| `at(pos)`                  | 访问指定字符（带边界检查）             | `s.at(2)`                  |
| `operator[](pos)`          | 下标访问（无边界检查）                 | `s[2]`                     |
| `front()` / `back()`       | 首/尾字符引用 (C++11)                  | `s.front()`                |
| `c_str()`                  | 返回 C 风格 `const char*`              | `s.c_str()`                |
| `data()`                   | 同 `c_str()` (C++11 起可写)            | `s.data()`                 |
| `substr(pos, count)`       | 取子串，默认到末尾                     | `s.substr(2, 3)`           |
| `append(str)`              | 追加字符串                             | `s.append("xyz")`          |
| `push_back(ch)`            | 追加一个字符                           | `s.push_back('!')`         |
| `pop_back()`               | 删除最后一个字符 (C++11)               | `s.pop_back()`             |
| `insert(pos, str)`         | 在 pos 前插入                          | `s.insert(2, "abc")`       |
| `erase(pos, count)`        | 删除从 pos 开始 count 个字符           | `s.erase(2, 3)`            |
| `replace(pos, count, str)` | 替换子串                               | `s.replace(0, 3, "new")`   |
| `find(str, pos)`           | 从 pos 开始查找子串，返回下标或 `npos` | `s.find("abc")`            |
| `rfind(str)`               | 从右向左查找                           | `s.rfind('c')`             |
| `find_first_of(chars)`     | 查找第一个属于给定集合的字符           | `s.find_first_of("aeiou")` |
| `find_first_not_of(chars)` | 查找第一个不属于给定集合的字符         |                            |
| `compare(str)`             | 与 str 比较，返回负数/0/正数           | `s.compare("abc")`         |

> **注意**：`npos` 是一个静态常量，值为 `size_t(-1)`，表示未找到。

### 3.1 示例：查找与替换

```cpp
string s = "hello world";
size_t pos = s.find("world");
if (pos != string::npos) {
    s.replace(pos, 5, "C++");
}
// s = "hello C++"
```

---

## 4. 相关全局函数与算法

需要包含头文件 `<cctype>`、`<algorithm>`、`<cstdlib>`（C++11 后使用 `<string>` 中的转换函数）。

### 4.1 字符判断与转换（`<cctype>`）

| 函数                        | 说明                            |
| --------------------------- | ------------------------------- |
| `isalpha(c)`                | 是否为字母                      |
| `isdigit(c)`                | 是否为数字                      |
| `isalnum(c)`                | 是否为字母或数字                |
| `islower(c)` / `isupper(c)` | 是否小/大写                     |
| `tolower(c)` / `toupper(c)` | 转换为小/大写（返回转换后的值） |

### 4.2 大小写转换示例

```cpp
#include <algorithm>
#include <cctype>

string s = "Hello World";
// 转小写
transform(s.begin(), s.end(), s.begin(), ::tolower);
// 转大写
transform(s.begin(), s.end(), s.begin(), ::toupper);
```

### 4.3 其他算法（`<algorithm>`）

```cpp
reverse(s.begin(), s.end());          // 反转字符串
sort(s.begin(), s.end());             // 按 ASCII 排序
unique(s.begin(), s.end());           // 去重（需先排序）
// 统计某个字符个数
count(s.begin(), s.end(), 'a');
```

### 4.4 数值与字符串互转（C++11）

```cpp
#include <string>
int i = stoi("123");          // string to int
long l = stol("123");
double d = stod("3.14");
string s = to_string(123);    // "123"
// 还有 stoll, stoul, stof, stold
```

---

## 5. 常见 OJ 题型与解题思路

### 题型一：字符串基础统计

**题目示例**：统计字符串中字母、数字、空格、其他字符的个数；判断大小写字母个数；统计单词数。

**核心方法**：遍历 + `isalpha`/`isdigit`/`isupper`/`islower`。

```cpp
string s;
getline(cin, s);
int upper = 0, lower = 0, digit = 0, space = 0;
for (char c : s) {
    if (isupper(c)) upper++;
    else if (islower(c)) lower++;
    else if (isdigit(c)) digit++;
    else if (isspace(c)) space++;
}
```

### 题型二：子串查找与替换

**题目示例**：查找子串出现次数；替换某子串为另一子串；删除所有指定字符。

**核心方法**：`find` 循环。

```cpp
// 查找子串出现次数
string s, pat;
size_t cnt = 0, pos = 0;
while ((pos = s.find(pat, pos)) != string::npos) {
    cnt++;
    pos += pat.size();  // 跳过已找到的子串
}
```

### 题型三：字符串反转 / 回文判断

**题目示例**：判断是否回文；反转字符串中的单词；反转指定区间。

**核心方法**：`reverse` 或双指针。

```cpp
// 回文判断
bool isPalindrome(const string& s) {
    int i = 0, j = s.size() - 1;
    while (i < j) {
        if (s[i] != s[j]) return false;
        i++; j--;
    }
    return true;
}
// 原地反转
reverse(s.begin(), s.end());
```

### 题型四：字符串分割

**题目示例**：以空格或逗号分割字符串；提取 IP 地址各段；解析 CSV。

**核心方法**：`find` + `substr`，或使用 `stringstream`。

```cpp
// 使用 stringstream 按空格分割
#include <sstream>
string s = "apple banana cherry";
stringstream ss(s);
string token;
while (ss >> token) {
    cout << token << endl;
}

// 自定义分隔符（如逗号）
vector<string> split(const string& s, char delim) {
    vector<string> res;
    size_t start = 0, end;
    while ((end = s.find(delim, start)) != string::npos) {
        res.push_back(s.substr(start, end - start));
        start = end + 1;
    }
    res.push_back(s.substr(start));
    return res;
}
```

### 题型五：字符串与数值转换

**题目示例**：字符串转整数（实现 `atoi`）；大数相加、相乘；进制转换。

**核心方法**：`stoi` / `to_string` 或模拟手算。

```cpp
// 大数相加（字符串形式）
string addStrings(string a, string b) {
    int i = a.size() - 1, j = b.size() - 1, carry = 0;
    string res = "";
    while (i >= 0 || j >= 0 || carry) {
        int sum = carry;
        if (i >= 0) sum += a[i--] - '0';
        if (j >= 0) sum += b[j--] - '0';
        res.push_back(sum % 10 + '0');
        carry = sum / 10;
    }
    reverse(res.begin(), res.end());
    return res;
}
```

### 题型六：字符去重与频率统计

**题目示例**：删除重复字符；输出出现次数最多的字符；判断是否为变位词。

**核心方法**：`sort` + `unique`，或 `int cnt[256]` 数组。

```cpp
// 统计每个字符频率
int freq[256] = {0};
for (char c : s) freq[(unsigned char)c]++;

// 排序后去重
sort(s.begin(), s.end());
s.erase(unique(s.begin(), s.end()), s.end());
```

### 题型七：字符串匹配

**题目示例**：朴素的子串匹配；KMP 算法（竞赛常用）。

**核心方法**：`find` 可直接应付简单题；复杂题实现 KMP。

```cpp
// KMP 的 next 数组构建（示例）
vector<int> buildNext(const string& pat) {
    int n = pat.size();
    vector<int> next(n, 0);
    for (int i = 1, j = 0; i < n; i++) {
        while (j > 0 && pat[i] != pat[j]) j = next[j-1];
        if (pat[i] == pat[j]) j++;
        next[i] = j;
    }
    return next;
}
```

### 题型八：字符串模拟类

**题目示例**：字符串压缩（如 `aabcccc` → `a2b1c4`）；字符串解码（如 `3[a2[c]]` → `accaccacc`）。

**核心方法**：栈、递归或线性扫描。

```cpp
// 字符串压缩（基础版）
string compress(string s) {
    string ans;
    int cnt = 1;
    for (int i = 0; i < s.size(); i++) {
        if (i + 1 < s.size() && s[i] == s[i+1]) cnt++;
        else {
            ans += s[i] + to_string(cnt);
            cnt = 1;
        }
    }
    return ans.size() < s.size() ? ans : s;
}
```

---

## 6. 注意事项

- **下标访问不检查边界**：使用 `at()` 可抛出 `out_of_range` 异常。
- **`size()` 返回 `size_t` 无符号类型**：与有符号数比较时易产生意外，推荐使用 `int i = 0; i < (int)s.size()` 或直接使用 `size_t`。
- **`find` 返回 `string::npos`**：不要用 `-1` 判断。
- **`c_str()` 返回的指针在 string 被修改或销毁后失效**。
- **多字节字符（中文）**：`char` 存储一个字节，中文可能占多个字节，`size()` 返回字节数而非字符数。处理中文建议使用 `wstring` 或 UTF-8 库。

---

## 7. 快速参考卡片

```cpp
// 常用头文件
#include <string>
#include <cctype>
#include <algorithm>
#include <sstream>

// 常用操作速查
s.size()
s.empty()
s.find(sub) != string::npos
s.substr(pos, len)
stoi(s)          // string to int
to_string(num)   // int to string
getline(cin, s)  // 读一行

// 大小写转换
transform(s.begin(), s.end(), s.begin(), ::tolower);

// 反转
reverse(s.begin(), s.end());

// 遍历
for (char c : s) { ... }
for (int i = 0; i < s.size(); ++i) { s[i]; }
```