// 建物の外観（フロア × 部屋）を描く。データは架空で固定（撮影のたびに同じ絵になる）
// 書式: [名前, 定員, 状態]  状態: 1=空き（灯る）, 0=使用中または条件外, 2=選択中
// 条件「14:00–15:00・6 名以上」で灯るのは 12 室（画面の件数と合わせてある）
const FLOORS = {
  "8F": [["欅",20,0],["楠",12,1],["樫",8,1],["椎",6,0],["榎",4,0],["桐",4,0]],
  "7F": [["楓",8,2],["椿",6,0],["柊",6,1],["桂",4,0],["杉",4,0],["檜",2,0]],
  "6F": [["松",12,0],["梅",8,1],["桜",6,1],["藤",6,0],["萩",4,0],["菫",2,0]],
  "5F": [["朝",10,0],["昼",8,1],["夕",6,1],["宵",4,0],["暁",4,0],["凪",2,0]],
  "4F": [["空",16,1],["海",8,1],["山",6,0],["川",4,0],["森",4,0],["丘",2,0]],
  "3F": [["一",30,0],["二",12,1],["三",8,1],["四",6,0],["五",4,0],["六",4,0]],
};
function drawFacade(el, opts = {}) {
  const cols = opts.cols || 6, labels = opts.labels !== false;
  let html = "";
  for (const [floor, rooms] of Object.entries(FLOORS)) {
    html += `<div class="floor" style="--n:${cols}"><div class="floor-no">${floor}</div>`;
    for (const [name, cap, st] of rooms.slice(0, cols)) {
      const cls = st === 0 ? "win busy" : st === 2 ? "win lit pick" : "win lit";
      html += `<div class="${cls}">${labels ? `<b>${name}</b><span>${cap}名</span>` : ""}</div>`;
    }
    html += "</div>";
  }
  el.innerHTML = html;
}
