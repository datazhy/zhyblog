/* ===========================================================
 * sw.js —— 自注销脚本
 * ===========================================================
 * 本站已停用 Service Worker（静态博客不需要离线缓存，
 * 且原先的 stale-while-revalidate 策略会让每次更新延迟一轮才生效）。
 *
 * 这个文件保留在原路径上，内容换成「自注销」逻辑：
 * 老访客浏览器在例行检查 sw.js 更新时会装上它，
 * 它会清空全部缓存并注销自身，从而让旧 SW 干净退出。
 *
 * 等历史缓存基本清理完毕后（约几个月），本文件可连同
 * js/sw-registration.js、js/snackbar.js、offline.html 一并删除。
 * ========================================================== */

self.addEventListener('install', function () {
    // 立即进入 activate，不等待旧 worker 释放
    self.skipWaiting();
});

self.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys()
            .then(function (keys) {
                return Promise.all(keys.map(function (key) {
                    return caches.delete(key);
                }));
            })
            .catch(function () { /* 缓存已不可用时忽略 */ })
            .then(function () {
                return self.registration.unregister();
            })
    );
});

// 不拦截任何请求：全部直接走网络
