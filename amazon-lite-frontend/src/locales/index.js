// src/locales/index.js
import { createI18n } from 'vue-i18n'

const messages = {
  // ==========================================
  // 🇨🇳 中文
  // ==========================================
  zh: {
    nav: {
      products: '产品目录',
      news: '行业资讯',
      contact: '联系我们',
      about: '关于我们',
      login: '登录 / 注册',
      admin: '后台管理',
      logout: '退出'
    },
    hero: {
      // 必须保证 slides 是一个数组，且有3个元素
      slides: [
        {
          tag: 'Global Energy Link',
          title: '连接世界的<br/><span class="text-orange-500">可靠动力</span>',
          subtitle: '高压与超高压输电解决方案全球领导者。'
        },
        {
          tag: 'Precision Manufacturing',
          title: '每一米都承载<br/><span class="text-orange-500">工业匠心</span>',
          subtitle: '全自动化生产线与严苛的质量检测体系。'
        },
        {
          tag: 'Future Ready Infrastructure',
          title: '赋能智慧城市与<br/><span class="text-orange-500">未来工业</span>',
          subtitle: '为新基建提供全方位的线缆支持。'
        }
      ],
      btn_stock: '查看现货库存',
      btn_contact: '联系销售经理'
    },
    home: {
      hot_products: '热门规格现货',
      hot_desc: '严格执行 GB/T 标准，精选热销型号',
      view_all_products: '查看全部产品',
      news_title: '行业资讯 & 动态',
      news_desc: '聚焦电力传输前沿技术，分享企业最新里程碑',
      view_all_news: '查看全部新闻',
      read_more: '阅读全文',
      stock: '现货',
      custom: '订制',
      price_unit: '/ 米'
    },
    footer: {
      desc: '作为全球基础设施建设的可靠合作伙伴，我们要致力于提供最优质的电力传输与信号控制解决方案。',
      links: '快速链接',
      manual: '下载选型手册',
      copper: '今日铜价',
      contact: '联系我们',
      rights: '© 2025 Amazon Cable Co., Ltd. 保留所有权利。'
    }
  },

  // ==========================================
  // 🇬🇧 英文 (务必补全 hero.slides)
  // ==========================================
  en: {
    nav: {
      products: 'Products',
      news: 'News',
      contact: 'Contact',
      about: 'About Us',
      login: 'Login / Register',
      admin: 'Dashboard',
      logout: 'Logout'
    },
    hero: {
      // 【关键修复】英文也必须有这个数组结构
      slides: [
        {
          tag: 'Global Energy Link',
          title: 'Connect the World with<br/><span class="text-orange-500">Reliable Power</span>',
          subtitle: 'Global leader in HV and EHV transmission solutions.'
        },
        {
          tag: 'Precision Manufacturing',
          title: 'Precision in<br/><span class="text-orange-500">Every Meter</span>',
          subtitle: 'Fully automated production lines with rigorous quality control.'
        },
        {
          tag: 'Future Ready Infrastructure',
          title: 'Empowering Smart Cities &<br/><span class="text-orange-500">Future Industry</span>',
          subtitle: 'Comprehensive cable support for new infrastructure projects.'
        }
      ],
      btn_stock: 'Check Stock',
      btn_contact: 'Contact Sales'
    },
    home: {
      hot_products: 'Hot Selling Specs',
      hot_desc: 'Strictly adhering to GB/T standards, selected best-selling models.',
      view_all_products: 'View All Products',
      news_title: 'Industry News & Updates',
      news_desc: 'Focusing on cutting-edge power transmission technology and sharing latest milestones.',
      view_all_news: 'View All News',
      read_more: 'Read More',
      stock: 'In Stock',
      custom: 'Pre-order',
      price_unit: '/ m'
    },
    footer: {
      desc: 'As a reliable partner for global infrastructure construction, we are committed to providing the highest quality power transmission and signal control solutions.',
      links: 'Quick Links',
      manual: 'Download Manual',
      copper: 'Copper Price',
      contact: 'Contact Us',
      rights: '© 2025 Amazon Cable Co., Ltd. All rights reserved.'
    }
  },

  // ==========================================
  // 🇰🇭 柬埔寨语 (务必补全 hero.slides)
  // ==========================================
  km: {
    nav: {
      products: 'ផលិតផល',
      news: 'ព័ត៌មាន',
      contact: 'ទំនាក់ទំនង',
      about: 'អំពីយើង',
      login: 'ចូល / ចុះឈ្មោះ',
      admin: 'គ្រប់គ្រង',
      logout: 'ចាកចេញ'
    },
    hero: {
      // 【关键修复】柬埔寨语也必须有这个数组结构
      slides: [
        {
          tag: 'Global Energy Link',
          title: 'ភ្ជាប់ពិភពលោកជាមួយ<br/><span class="text-orange-500">ថាមពលដែលអាចទុកចិត្តបាន</span>',
          subtitle: 'អ្នកដឹកនាំពិភពលោកក្នុងការបញ្ជូនថាមពលតង់ស្យុងខ្ពស់។'
        },
        {
          tag: 'Precision Manufacturing',
          title: 'ភាពច្បាស់លាស់នៅ<br/><span class="text-orange-500">គ្រប់ម៉ែត្រ</span>',
          subtitle: 'ខ្សែសង្វាក់ផលិតកម្មដោយស្វ័យប្រវត្តិ ជាមួយនឹងការត្រួតពិនិត្យគុណភាពយ៉ាងតឹងរ៉ឹង។'
        },
        {
          tag: 'Future Ready Infrastructure',
          title: 'ផ្តល់ថាមពលដល់ទីក្រុងឆ្លាតវៃ &<br/><span class="text-orange-500">ឧស្សាហកម្មនាពេលអនាគត</span>',
          subtitle: 'ការគាំទ្រខ្សែដ៏ទូលំទូលាយសម្រាប់គម្រោងហេដ្ឋារចនាសម្ព័ន្ធថ្មី។'
        }
      ],
      btn_stock: 'ពិនិត្យស្តុក',
      btn_contact: 'ទាក់ទងផ្នែកលក់'
    },
    home: {
      hot_products: 'លក្ខណៈបច្ចេកទេសពេញនិយម',
      hot_desc: 'អនុវត្តតាមស្តង់ដារ GB/T យ៉ាងតឹងរឹង ម៉ូដែលដែលលក់ដាច់បំផុត។',
      view_all_products: 'មើលផលិតផលទាំងអស់',
      news_title: 'ព័ត៌មានឧស្សាហកម្ម & បច្ចុប្បន្នភាព',
      news_desc: 'ផ្តោតលើបច្ចេកវិទ្យាបញ្ជូនថាមពល និងចែករំលែកសមិទ្ធផលចុងក្រោយ។',
      view_all_news: 'មើលព័ត៌មានទាំងអស់',
      read_more: 'អាន​បន្ថែម',
      stock: 'មានស្តុក',
      custom: 'កុម្ម៉ង់',
      price_unit: '/ ម៉ែត្រ'
    },
    footer: {
      desc: 'ក្នុងនាមជាដៃគូដែលអាចទុកចិត្តបានសម្រាប់ការកសាងហេដ្ឋារចនាសម្ព័ន្ធពិភពលោក យើងប្តេជ្ញាផ្តល់ជូននូវដំណោះស្រាយបញ្ជូនថាមពល និងគ្រប់គ្រងសញ្ញាដែលមានគុណភាពខ្ពស់បំផុត។',
      links: 'តំណភ្ជាប់រហ័ស',
      manual: 'ទាញយកសៀវភៅដៃ',
      copper: 'តម្លៃស្ពាន់ថ្ងៃនេះ',
      contact: 'ទាក់ទង​មក​ពួក​យើង',
      rights: '© 2025 Amazon Cable Co., Ltd. រក្សាសិទ្ធិគ្រប់យ៉ាង។'
    }
  }
}

// 创建 i18n 实例
const i18n = createI18n({
  legacy: false, 
  locale: localStorage.getItem('lang') || 'zh', 
  fallbackLocale: 'en', 
  globalInjection: true,
  // 【关键修复】关闭 HTML 警告，因为我们是有意使用 HTML 样式的
  warnHtmlMessage: false, 
  messages
})

export default i18n