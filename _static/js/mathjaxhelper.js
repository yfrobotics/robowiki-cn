window.MathJax = {
  loader: {
    load: ['[tex]/tagformat']
  },
  startup: {
    pageReady: () => {
      alert('Running MathJax');
      return MathJax.startup.defaultPageReady();
    }
  },
  tex: {
    inlineMath: [['$','$'], ['\\(','\\)']],
    autoload: {
        color: [],
        colorV2: ['color']
    },
    packages: {'[+]': ['enclose'], '[-]': ['autoload', 'require']},
    tagSide: 'left',
    macros: {
      RR: '{\\bf R}',
      bold: ['{\\bf #1}',1]
    },
    tagformat: {
       tag: (n) => '[' + n + ']'
    }
  }
};
