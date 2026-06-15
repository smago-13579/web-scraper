export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Перенаправляем все запросы на официальный API Telegram
    const targetUrl = 'https://api.telegram.org' + url.pathname + url.search;

    // Копируем исходный запрос (метод, заголовки, тело)
    const modifiedRequest = new Request(targetUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body
    });

    // Возвращаем ответ от Telegram обратно вашему боту
    return fetch(modifiedRequest);
  },
};
