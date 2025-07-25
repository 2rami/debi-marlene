(self.webpackChunk_N_E = self.webpackChunk_N_E || []).push([[2275], {
    83726: function(n, e, t) {
        (window.__NEXT_P = window.__NEXT_P || []).push(["/players/[name]", function() {
            return t(83603)
        }
        ])
    },
    83603: function(n, e, t) {
        "use strict";
        t.r(e),
        t.d(e, {
            __N_SSP: function() {
                return ft
            },
            default: function() {
                return ut
            }
        });
        var a = t(7297)
          , i = t(85893)
          , r = t(67294)
          , l = t(1922)
          , o = t(2962)
          , s = t(33786)
          , c = t(94184)
          , d = t.n(c)
          , p = t(77958)
          , x = t(24082)
          , h = t(75612)
          , f = t(60190)
          , u = t(85345)
          , g = t(28297)
          , m = t(14599)
          , v = t(25947)
          , j = t(63768)
          , y = t(93293)
          , w = function(n) {
            var e = {
                plays: 0,
                avgDamageToPlayer: 0,
                winRate: 0,
                wins: 0,
                defeats: 0,
                avgKill: 0,
                avgAssist: 0,
                avgAnimalKill: 0,
                avgDamageToAnimal: 0,
                avgTeamKill: 0,
                top2: 0,
                top3: 0,
                avgRank: 0
            }
              , t = {
                plays: void 0,
                avgDamageToPlayer: void 0,
                winRate: void 0,
                wins: void 0,
                defeats: void 0,
                avgKill: void 0,
                avgAssist: void 0,
                avgAnimalKill: void 0,
                avgDamageToAnimal: void 0,
                avgTeamKill: void 0,
                top2: void 0,
                top3: void 0,
                avgRank: void 0
            }
              , a = {
                globalRank: 0,
                globalRatio: "0.00",
                localRank: 0,
                localRatio: "0.00",
                localName: ""
            };
            if (n) {
                var i, r, l, o, s, c, d, p = n.place / n.play, x = n.playerKill / n.play, h = n.playerAssistant / n.play, f = n.teamKill / n.play;
                e = {
                    plays: 0 === n.play ? 0 : n.play >= 30 ? 100 : n.play / 30 * 100,
                    avgDamageToPlayer: n.damageToPlayer > 0 ? 100 : 0,
                    winRate: n.win / n.play * 100,
                    wins: n.win / n.play * 100,
                    defeats: (n.play - n.win) / n.play * 100,
                    avgKill: 0 === x ? 0 : x >= 3 ? 100 : x / 3 * 100,
                    avgAssist: 0 === h ? 0 : h >= 5 ? 100 : h / 5 * 100,
                    avgAnimalKill: n.monsterKill > 0 ? 100 : 0,
                    avgDamageToAnimal: n.damageToMonster > 0 ? 100 : 0,
                    avgTeamKill: 0 === f ? 0 : f >= 7 ? 100 : f / 7 * 100,
                    top2: n.top2 / n.play * 100,
                    top3: n.top3 / n.play * 100,
                    avgRank: 0 === p || p >= 10 ? 0 : 100 - (p - 1) / 10 * 100
                },
                t = {
                    plays: n.play,
                    avgDamageToPlayer: (0,
                    y.JG)(n.damageToPlayer / n.play),
                    winRate: (0,
                    y._f)(n.win, n.play),
                    wins: n.win,
                    defeats: n.play - n.win,
                    avgKill: (0,
                    y.RD)(x),
                    avgAssist: (0,
                    y.n_)(h),
                    avgAnimalKill: (0,
                    y.RD)(n.monsterKill / n.play),
                    avgDamageToAnimal: (0,
                    y.JG)(n.damageToMonster / n.play),
                    avgTeamKill: (0,
                    y.RD)(f),
                    top2: (0,
                    y._f)(n.top2, n.play),
                    top3: (0,
                    y._f)(n.top3, n.play),
                    avgRank: (0,
                    y.ZD)(p)
                };
                var u = Number(null !== (d = null === (i = n.rank) || void 0 === i || null === (r = i.in1000) || void 0 === r ? void 0 : r.rank) && void 0 !== d ? d : 0) > 0;
                if (u && (null === (l = n.rank) || void 0 === l ? void 0 : l.in1000)) {
                    var g = n.rank.in1000.rank
                      , m = n.rank.in1000.rankSize
                      , v = m > 0 ? (g / m * 100).toFixed(2) : "-";
                    a.globalRank = g,
                    a.globalRatio = "0.00" === v ? "0.01" : v
                }
                if (!u && (null === (o = n.rank) || void 0 === o ? void 0 : o.global)) {
                    var w = n.rank.global.rank
                      , b = n.rank.global.rankSize
                      , k = b > 0 ? (w / b * 100).toFixed(2) : "-";
                    a.globalRank = w,
                    a.globalRatio = "0.00" === k ? "0.01" : k
                }
                if (null === (s = n.rank) || void 0 === s ? void 0 : s.local) {
                    var C = n.rank.local.rank
                      , N = n.rank.local.rankSize
                      , Z = N > 0 ? (C / N * 100).toFixed(2) : "-";
                    a.localRank = C,
                    a.localRatio = "0.00" === Z ? "0.01" : a.globalRatio
                }
                var M, R = n.serverStats.length > 0 ? n.serverStats[0].key : void 0, A = R && null !== (M = null === (c = j.a.find((function(n) {
                    return n.key === R.trim().toLowerCase()
                }
                ))) || void 0 === c ? void 0 : c.name) && void 0 !== M ? M : "";
                a.localName = A
            }
            return {
                formatStats: t,
                percents: e,
                rankInfo: a
            }
        }
          , b = t(8579)
          , k = t(33206);
        function C() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  flex-direction: column;\n  row-gap: 6px;\n  font-size: 12px;\n  line-height: 12px;\n\n  > .percent-bar {\n    position: relative;\n    width: 100%;\n    background: #e6e6e6;\n    border-radius: 4px;\n    height: 4px;\n\n    > div {\n      position: absolute;\n      left: 0;\n      top: 0;\n      height: 100%;\n      border-radius: 4px;\n\n      background: ", ";\n    }\n  }\n\n  > h4 {\n    color: #808080;\n  }\n\n  > .value {\n    font-weight: 600;\n    color: #646464;\n  }\n"]);
            return C = function() {
                return n
            }
            ,
            n
        }
        var N = function(n) {
            var e = n.title
              , t = n.percent
              , a = n.value
              , r = n.color;
            return (0,
            i.jsxs)(Z, {
                color: r,
                children: [(0,
                i.jsx)("h4", {
                    children: e
                }), (0,
                i.jsx)("div", {
                    className: "percent-bar",
                    children: (0,
                    i.jsx)("div", {
                        style: {
                            width: "".concat(t || 0, "%")
                        }
                    })
                }), (0,
                i.jsx)("div", {
                    className: "value",
                    children: a || "-"
                })]
            })
        }
          , Z = s.Z.div(C(), (function(n) {
            switch (n.color) {
            case "gray":
            default:
                return "#666a7a";
            case "green":
                return "#11b288";
            case "blue":
                return "#207AC7"
            }
        }
        ))
          , M = t(29815)
          , R = t(66775)
          , A = t(55376);
        function S() {
            var n = (0,
            a.Z)(["\n  width: 100%;\n  height: 150px;\n"]);
            return S = function() {
                return n
            }
            ,
            n
        }
        R.kL.register(R.uw, R.f$, R.od, R.jn, R.Dx, R.u, R.De);
        var L = {
            id: "lineAt",
            beforeDraw: function(n) {
                var e, t;
                if ("undefined" !== typeof (null === n || void 0 === n || null === (e = n.config) || void 0 === e || null === (t = e.options) || void 0 === t ? void 0 : t.lineAt)) {
                    var a, i, r = null === n || void 0 === n || null === (a = n.config) || void 0 === a || null === (i = a.options) || void 0 === i ? void 0 : i.lineAt, l = null === n || void 0 === n ? void 0 : n.ctx, o = n.scales.y;
                    l.strokeStyle = "#e6e6e6",
                    l.beginPath(),
                    l.setLineDash([1, 1]),
                    r = o.getPixelForValue(r),
                    l.moveTo(45, r),
                    l.lineTo(n.width - 17, r),
                    l.stroke()
                }
            }
        }
          , D = function(n) {
            var e, t, a, r = n.mmrStats, o = n.teamModeId, s = (0,
            l.$G)(["common", "player"]).t, c = r.sort((function(n, e) {
                return n[0] - e[0]
            }
            )).slice(-7), d = c.map((function(n) {
                return function(n) {
                    var e = n % 100
                      , t = Math.floor(n % 1e4 / 100).toString().padStart(2, "0")
                      , a = e.toString().padStart(2, "0");
                    return "".concat(t, "/").concat(a)
                }(n[0])
            }
            )), p = null !== (a = c.map((function(n) {
                return null !== (t = n[1]) && void 0 !== t ? t : 0
            }
            ))) && void 0 !== a ? a : [], x = 1 === o ? "#5393ca" : 2 === o ? "#748e3a" : "#ca9372", h = {
                interaction: {
                    mode: "index",
                    intersect: !1
                },
                maintainAspectRatio: !1,
                plugins: {
                    legend: {
                        display: !1
                    },
                    title: {
                        text: s("player:chartTitle")
                    },
                    tooltip: {
                        displayColors: !1,
                        callbacks: {
                            title: function(n) {
                                return "".concat(s("player:lastMmr"), " ").concat(n[0].raw)
                            },
                            label: function(n) {
                                return "".concat(s("player:minMmr"), " : ").concat(c[n.dataIndex][2], ", ").concat(s("player:maxMmr"), " : ").concat(c[n.dataIndex][3])
                            }
                        }
                    }
                },
                lineAt: (e = Math).min.apply(e, (0,
                M.Z)(p)),
                scales: {
                    x: {
                        ticks: {
                            color: "#999",
                            font: {
                                size: 11,
                                family: "Pretendard, sans-serif, -apple-system"
                            }
                        },
                        grid: {
                            display: !1
                        }
                    },
                    y: {
                        ticks: {
                            color: "#999",
                            font: {
                                size: 11,
                                family: "Pretendard, sans-serif, -apple-system"
                            },
                            stepSize: 100,
                            maxTicksLimit: 6
                        },
                        grid: {
                            display: !1
                        }
                    }
                }
            }, f = {
                labels: d,
                datasets: [{
                    fill: !1,
                    data: p,
                    borderColor: x,
                    backgroundColor: x,
                    borderWidth: 1,
                    pointRadius: 2,
                    tension: 0
                }]
            };
            return (0,
            i.jsx)(B, {
                children: (0,
                i.jsx)(A.x1, {
                    options: h,
                    data: f,
                    plugins: [L]
                })
            })
        }
          , B = s.Z.div(S());
        function z() {
            var n = (0,
            a.Z)(["\n  border: 1px solid #e6e6e6;\n  background: #ffffff;\n\n  > header {\n    padding: ", ";\n    border-bottom: ", ";\n    background: ", ";\n\n    > h2 {\n      font-size: 14px;\n      font-weight: 600;\n      line-height: 14px;\n      color: ", ";\n      text-align: center;\n    }\n  }\n\n  > .graph-wrapper {\n    height: 169px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    padding: 16px;\n    width: 100%;\n\n    > .play-rank {\n      font-size: 12px;\n      font-weight: 400;\n      line-height: 16px;\n      color: #808080;\n    }\n  }\n"]);
            return z = function() {
                return n
            }
            ,
            n
        }
        function T() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  justify-content: center;\n  align-items: center;\n  column-gap: 12px;\n  padding: 16px 19px 20px 19px;\n  height: 106px;\n\n  > img {\n    width: 64px;\n    height: 64px;\n  }\n\n  > div {\n    display: flex;\n    flex-direction: column;\n    row-gap: 6px;\n\n    &.no-record {\n      font-size: 12px;\n      line-height: 12px;\n      color: #808080;\n\n      > .unranked {\n        color: #646464;\n        font-weight: 600;\n      }\n    }\n\n    > b.rp {\n      color: #ca9372;\n      font-size: 16px;\n      font-weight: 600;\n      line-height: 16px;\n\n      > span {\n        margin-left: 2px;\n      }\n    }\n\n    > div {\n      font-size: 12px;\n      line-height: 12px;\n      color: #808080;\n\n      &.tier {\n        font-weight: 600;\n        color: #646464;\n      }\n    }\n  }\n"]);
            return T = function() {
                return n
            }
            ,
            n
        }
        function K() {
            var n = (0,
            a.Z)(["\n  padding: 15px 19px;\n  border-top: 1px solid #e6e6e6;\n  border-bottom: ", ";\n  display: grid;\n  gap: 12px;\n  grid-template-columns: 1fr 1fr 1fr;\n\n  ", " {\n    grid-template-columns: 1fr 1fr 1fr 1fr 1fr;\n  }\n\n  ", " {\n    grid-template-columns: 1fr 1fr 1fr;\n  }\n"]);
            return K = function() {
                return n
            }
            ,
            n
        }
        var E = function(n) {
            var e = n.teamMode
              , t = void 0 === e ? "SQUAD" : e
              , a = n.isEarly
              , o = (0,
            l.$G)("player").t
              , s = (0,
            g.Z)()
              , c = s.name
              , d = s.seasonQuery
              , p = (0,
            v.f)(c).data
              , x = (0,
            m.ST)().data
              , h = b.AN.RANK
              , f = b.Vo[t]
              , u = (0,
            r.useMemo)((function() {
                var n;
                if (p) {
                    var e = null === (n = p.playerSeasonOverviews) || void 0 === n ? void 0 : n.find((function(n) {
                        return n.matchingModeId === h && n.teamModeId === f
                    }
                    ));
                    return e
                }
            }
            ), [p, h, f])
              , j = w(u)
              , y = j.formatStats
              , C = j.percents
              , Z = j.rankInfo
              , M = "SEASON_1" === d
              , R = null === x || void 0 === x ? void 0 : x.tiers.find((function(n) {
                return n.id === (null === u || void 0 === u ? void 0 : u.tierId)
            }
            ));
            return (0,
            i.jsxs)(_, {
                isEarly: a,
                teamMode: t,
                children: [(0,
                i.jsx)("header", {
                    children: (0,
                    i.jsx)("h2", {
                        children: o(a ? "teamMode.".concat(t.toLowerCase()) : "gameMode.rank")
                    })
                }), (0,
                i.jsxs)(O, {
                    children: [R ? (0,
                    i.jsx)("img", {
                        src: null === R || void 0 === R ? void 0 : R.iconUrl,
                        alt: null === R || void 0 === R ? void 0 : R.name
                    }) : (0,
                    i.jsx)("img", {
                        src: "".concat(k.DX, "/tier/round/0.png"),
                        alt: o("tier.unranked")
                    }), u ? (0,
                    i.jsxs)("div", {
                        children: [(0,
                        i.jsxs)("b", {
                            className: "rp",
                            children: [u.mmr, (0,
                            i.jsx)("span", {
                                children: "RP"
                            })]
                        }), (0,
                        i.jsxs)("div", {
                            className: "tier",
                            children: [R ? (0,
                            b.TF)(R, u.tierGradeId) : o("tier.unranked"), " - ", u.tierMmr, " RP"]
                        }), (0,
                        i.jsxs)("div", {
                            className: "rank",
                            children: [o("rank", {
                                rank: Z.globalRank ? (0,
                                b.Ew)(Z.globalRank) : "- "
                            }), " ", o("topRate", {
                                topRate: Z.globalRatio
                            })]
                        }), (0,
                        i.jsxs)("div", {
                            className: "local-rank",
                            children: [Z.localName, " ", o("rank", {
                                rank: Z.localRank ? (0,
                                b.Ew)(Z.localRank) : "- "
                            }), " ", o("topRate", {
                                topRate: Z.localRatio
                            })]
                        })]
                    }) : (0,
                    i.jsxs)("div", {
                        className: "no-record",
                        children: [(0,
                        i.jsx)("div", {
                            className: "unranked",
                            children: o("tier.unranked")
                        }), (0,
                        i.jsx)("div", {
                            children: o("noRecord")
                        })]
                    })]
                }), (0,
                i.jsxs)(P, {
                    isFirstSeason: M,
                    children: [(0,
                    i.jsx)(N, {
                        percent: C.avgTeamKill,
                        title: o("statCategory.avgTK"),
                        value: y.avgTeamKill
                    }), (0,
                    i.jsx)(N, {
                        percent: C.winRate,
                        title: o("statCategory.winRate"),
                        value: y.winRate,
                        color: "green"
                    }), (0,
                    i.jsx)(N, {
                        percent: C.plays,
                        title: o("statCategory.plays"),
                        value: y.plays
                    }), (0,
                    i.jsx)(N, {
                        percent: C.avgKill,
                        title: o("statCategory.avgKills"),
                        value: y.avgKill
                    }), (0,
                    i.jsx)(N, {
                        percent: C.top2,
                        title: o("statCategory.top2"),
                        value: y.top2,
                        color: "blue"
                    }), (0,
                    i.jsx)(N, {
                        percent: C.avgDamageToPlayer,
                        title: o("statCategory.avgDamage"),
                        value: y.avgDamageToPlayer
                    }), (0,
                    i.jsx)(N, {
                        percent: C.avgAssist,
                        title: o("statCategory.avgAssi"),
                        value: y.avgAssist
                    }), (0,
                    i.jsx)(N, {
                        percent: C.top3,
                        title: o("statCategory.top3"),
                        value: y.top3,
                        color: "blue"
                    }), (0,
                    i.jsx)(N, {
                        percent: C.avgRank,
                        title: o("statCategory.avgRank"),
                        value: y.avgRank
                    })]
                }), !M && (0,
                i.jsx)("div", {
                    className: "graph-wrapper",
                    children: u && u.mmrStats.length > 0 ? (0,
                    i.jsx)(D, {
                        mmrStats: u.mmrStats,
                        teamModeId: u.teamModeId
                    }) : (0,
                    i.jsx)("div", {
                        className: "play-rank",
                        children: o("playRank")
                    })
                })]
            })
        }
          , _ = s.Z.section(z(), (function(n) {
            return n.isEarly ? "14px 0px 15px" : "14px 0px 14px"
        }
        ), (function(n) {
            return n.isEarly ? "none" : "1px solid #e6e6e6"
        }
        ), (function(n) {
            var e = n.isEarly
              , t = n.teamMode;
            return e ? "SOLO" === t ? "#CA9372" : "DUO" === t ? "#5393CA" : "SQUAD" === t ? "#759716" : void 0 : "#ffffff"
        }
        ), (function(n) {
            return n.isEarly ? "#ffffff" : "#646464"
        }
        ))
          , O = s.Z.div(T())
          , P = s.Z.div(K(), (function(n) {
            return n.isFirstSeason ? "none" : "1px solid #e6e6e6"
        }
        ), f.B2.md, f.B2.lg)
          , G = t(41664)
          , F = t.n(G)
          , I = t(96486)
          , $ = t(47795);
        function U() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  align-items: center;\n  justify-content: center;\n  border-radius: 4px;\n  width: 28px;\n  height: 28px;\n\n  font-size: 12px;\n  font-weight: 600;\n  line-height: 12px;\n\n  background: ", ";\n\n  color: ", ";\n"]);
            return U = function() {
                return n
            }
            ,
            n
        }
        function Q() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  align-items: center;\n  justify-content: center;\n  border-radius: 4px;\n  width: 28px;\n  height: 28px;\n  background: #e6e6e6;\n  color: #808080;\n"]);
            return Q = function() {
                return n
            }
            ,
            n
        }
        var q = function(n) {
            var e = n.isEscape
              , t = n.isNull
              , a = n.rank
              , r = n.isCobalt
              , o = (0,
            l.$G)("player").t;
            return t ? (0,
            i.jsx)(X, {
                children: "-"
            }) : (0,
            i.jsx)(V, {
                rank: a,
                isEscape: e,
                isCobalt: r,
                children: e ? (0,
                i.jsx)($.Z, {
                    fill: "white",
                    size: 16
                }) : r ? o(1 === a ? "win" : "lose") : a
            })
        }
          , V = s.Z.div(U(), (function(n) {
            var e = n.rank
              , t = n.isEscape;
            return n.isCobalt ? 1 === e ? "#11B288" : "#D6D6D6" : t ? "#475482" : (0,
            I.isNumber)(e) ? 1 === e ? "#11B288" : e > 1 && e <= 3 ? "#207AC7" : "#D6D6D6" : void 0
        }
        ), (function(n) {
            var e = n.rank
              , t = n.isEscape;
            return n.isCobalt ? 1 === e ? "#ffffff" : "#808080" : t ? "#ffffff" : (0,
            I.isNumber)(e) ? 1 === e || e > 1 && e <= 3 ? "#ffffff" : "#808080" : void 0
        }
        ))
          , X = s.Z.div(Q());
        function H() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  align-items: center;\n  flex-direction: column;\n  row-gap: 6px;\n  font-size: 12px;\n  line-height: 12px;\n  width: 100%;\n\n  > h4 {\n    width: 100%;\n    font-size: 12px;\n    font-weight: 400;\n    line-height: 12px;\n    padding: 8px;\n    background: #f5f5f5;\n    color: #646464;\n    border-radius: 28px;\n    text-align: center;\n    margin-bottom: 16px;\n  }\n\n  > .match-item-wrapper {\n    width: 324px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    gap: 4px;\n    flex-wrap: wrap;\n\n    ", " {\n      width: 100%;\n    }\n\n    ", " {\n      width: 316px;\n    }\n  }\n"]);
            return H = function() {
                return n
            }
            ,
            n
        }
        var W = function(n) {
            var e = n.matches
              , t = n.isCobalt
              , a = (0,
            l.$G)("player").t
              , r = Array.from({
                length: 20 - e.length
            });
            return (0,
            i.jsxs)(Y, {
                children: [(0,
                i.jsx)("h4", {
                    children: a("recentMatches")
                }), (0,
                i.jsxs)("div", {
                    className: "match-item-wrapper",
                    children: [e.map((function(n, e) {
                        return (0,
                        i.jsx)(q, {
                            rank: n.rank,
                            isEscape: n.isEscape,
                            isCobalt: t
                        }, e)
                    }
                    )), r.map((function(n, e) {
                        return (0,
                        i.jsx)(q, {
                            isNull: !0
                        }, e)
                    }
                    ))]
                })]
            })
        }
          , Y = s.Z.div(H(), f.B2.md, f.B2.xl);
        function J() {
            var n = (0,
            a.Z)(["\n  border: 1px solid #e6e6e6;\n  background: #ffffff;\n\n  > header {\n    padding: 14px 0px 14px;\n    border-bottom: 1px solid #e6e6e6;\n\n    > h2 {\n      display: flex;\n      align-items: center;\n      justify-content: center;\n      gap: 2px;\n\n      font-size: 14px;\n      font-weight: 600;\n      line-height: 14px;\n      color: #646464;\n      text-align: center;\n\n      > span {\n        font-size: 12px;\n        font-weight: 400;\n        line-height: 12px;\n        color: #808080;\n      }\n    }\n  }\n\n  > .recent-match-wrapper {\n    height: 169px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    padding: 0px 17px;\n  }\n\n  > .total-stat-link {\n    display: block;\n    background: #464188;\n    width: 100%;\n    color: #ffffff;\n    text-align: center;\n    padding: 12px;\n    font-size: 14px;\n    line-height: 14px;\n\n    &.recent {\n      background: #88414f;\n    }\n  }\n"]);
            return J = function() {
                return n
            }
            ,
            n
        }
        function nn() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  justify-content: center;\n  align-items: center;\n  column-gap: 12px;\n  padding: 16px 19px 20px 19px;\n  height: 106px;\n\n  > img {\n    width: 64px;\n    height: 64px;\n  }\n\n  > div {\n    display: flex;\n    flex-direction: column;\n    row-gap: 6px;\n\n    &.no-record {\n      font-size: 12px;\n      line-height: 12px;\n      color: #808080;\n    }\n\n    > div {\n      display: flex;\n      font-size: 12px;\n      font-weight: 600;\n      line-height: 12px;\n      gap: 4px;\n\n      > b {\n        font-weight: 600;\n        color: #646464;\n      }\n\n      > span {\n        color: #808080;\n      }\n    }\n  }\n"]);
            return nn = function() {
                return n
            }
            ,
            n
        }
        function en() {
            var n = (0,
            a.Z)(["\n  padding: 15px 19px;\n  border-top: 1px solid #e6e6e6;\n  border-bottom: ", ";\n  display: grid;\n  gap: 12px;\n  grid-template-columns: 1fr 1fr 1fr;\n\n  ", " {\n    grid-template-columns: 1fr 1fr 1fr 1fr 1fr;\n  }\n\n  ", " {\n    grid-template-columns: 1fr 1fr 1fr;\n  }\n"]);
            return en = function() {
                return n
            }
            ,
            n
        }
        var tn = function(n) {
            var e, t = n.teamMode, a = void 0 === t ? "SQUAD" : t, o = n.hideBottom, s = (0,
            l.$G)("player").t, c = (0,
            g.Z)(), d = c.name, p = c.isNormalSeason, x = c.isLegacySeason, h = (0,
            v.f)(d).data, f = (0,
            m.dN)().data, u = b.AN.NORMAL, j = b.Vo[a], y = (0,
            r.useMemo)((function() {
                var n;
                if (h) {
                    var e = null === (n = h.playerSeasonOverviews) || void 0 === n ? void 0 : n.find((function(n) {
                        return n.matchingModeId === u && n.teamModeId === j
                    }
                    ));
                    return e
                }
            }
            ), [h, u, j]), C = (0,
            r.useMemo)((function() {
                return y ? y.recentMatches.map((function(n) {
                    return {
                        rank: n.gameRank,
                        isEscape: 3 === n.escapeState
                    }
                }
                )) : []
            }
            ), [y]), Z = w(y), M = Z.formatStats, R = Z.percents, A = null === (e = null === f || void 0 === f ? void 0 : f.seasons.find((function(n) {
                return n.key === (null === h || void 0 === h ? void 0 : h.meta.season)
            }
            ))) || void 0 === e ? void 0 : e.name;
            return (0,
            i.jsxs)(an, {
                children: [(0,
                i.jsx)("header", {
                    children: (0,
                    i.jsxs)("h2", {
                        children: [s("gameMode.normal"), (0,
                        i.jsxs)("span", {
                            children: ["(", p ? s("gameMode.total") : A, ")"]
                        })]
                    })
                }), (0,
                i.jsxs)(rn, {
                    children: [(0,
                    i.jsx)("img", {
                        src: "".concat(k.DX, "/common/img-gamemode-normal.png"),
                        alt: s("gameMode.normal")
                    }), y ? (0,
                    i.jsxs)("div", {
                        children: [(0,
                        i.jsxs)("div", {
                            children: [(0,
                            i.jsx)("b", {
                                children: s("statCategory.plays")
                            }), (0,
                            i.jsx)("span", {
                                children: M.plays
                            })]
                        }), (0,
                        i.jsxs)("div", {
                            children: [(0,
                            i.jsx)("b", {
                                children: s("statCategory.avgRank")
                            }), (0,
                            i.jsx)("span", {
                                children: M.avgRank
                            })]
                        }), (0,
                        i.jsxs)("div", {
                            children: [(0,
                            i.jsx)("b", {
                                children: s("statCategory.winRate")
                            }), (0,
                            i.jsx)("span", {
                                children: M.winRate
                            })]
                        })]
                    }) : (0,
                    i.jsx)("div", {
                        className: "no-record",
                        children: s("noRecord")
                    })]
                }), (0,
                i.jsxs)(ln, {
                    hideBottom: p || o,
                    children: [(0,
                    i.jsx)(N, {
                        percent: R.avgTeamKill,
                        title: s("statCategory.avgTK"),
                        value: M.avgTeamKill
                    }), (0,
                    i.jsx)(N, {
                        percent: R.winRate,
                        title: s("statCategory.winRate"),
                        value: M.winRate,
                        color: "green"
                    }), (0,
                    i.jsx)(N, {
                        percent: R.plays,
                        title: s("statCategory.plays"),
                        value: M.plays
                    }), (0,
                    i.jsx)(N, {
                        percent: R.avgKill,
                        title: s("statCategory.avgKills"),
                        value: M.avgKill
                    }), (0,
                    i.jsx)(N, {
                        percent: R.top2,
                        title: s("statCategory.top2"),
                        value: M.top2,
                        color: "blue"
                    }), (0,
                    i.jsx)(N, {
                        percent: R.avgDamageToPlayer,
                        title: s("statCategory.avgDamage"),
                        value: M.avgDamageToPlayer
                    }), (0,
                    i.jsx)(N, {
                        percent: R.avgAssist,
                        title: s("statCategory.avgAssi"),
                        value: M.avgAssist
                    }), (0,
                    i.jsx)(N, {
                        percent: R.top3,
                        title: s("statCategory.top3"),
                        value: M.top3,
                        color: "blue"
                    }), (0,
                    i.jsx)(N, {
                        percent: R.avgRank,
                        title: s("statCategory.avgRank"),
                        value: M.avgRank
                    })]
                }), !p && !o && (0,
                i.jsx)("div", {
                    className: "recent-match-wrapper",
                    children: (0,
                    i.jsx)(W, {
                        matches: C
                    })
                }), !p && !x && (0,
                i.jsx)(F(), {
                    href: "/players/".concat(d, "?season=NORMAL"),
                    children: (0,
                    i.jsx)("a", {
                        className: "total-stat-link",
                        children: s("viewTotalStatistics")
                    })
                }), p && (0,
                i.jsx)(F(), {
                    href: "/players/".concat(d, "?gameMode=NORMAL"),
                    children: (0,
                    i.jsx)("a", {
                        className: "total-stat-link recent",
                        children: s("viewRecentStatistics")
                    })
                })]
            })
        }
          , an = s.Z.section(J())
          , rn = s.Z.div(nn())
          , ln = s.Z.div(en(), (function(n) {
            return n.hideBottom ? "none" : "1px solid #e6e6e6"
        }
        ), f.B2.md, f.B2.lg);
        function on() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  flex-direction: column;\n  border: 1px solid #e6e6e6;\n  background: #ffffff;\n\n  > header {\n    padding: 14px 0px 14px;\n    border-bottom: 1px solid #e6e6e6;\n\n    > h2 {\n      display: flex;\n      align-items: center;\n      justify-content: center;\n      gap: 2px;\n\n      font-size: 14px;\n      font-weight: 600;\n      line-height: 14px;\n      color: #646464;\n      text-align: center;\n\n      > span {\n        font-size: 12px;\n        font-weight: 400;\n        line-height: 12px;\n        color: #808080;\n      }\n    }\n  }\n\n  > .recent-match-wrapper {\n    height: 169px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    padding: 0px 17px;\n  }\n\n  > .total-stat-link {\n    display: block;\n    background: #464188;\n    width: 100%;\n    color: #ffffff;\n    text-align: center;\n    padding: 12px;\n    font-size: 14px;\n    line-height: 14px;\n\n    &.recent {\n      background: #88414f;\n    }\n  }\n"]);
            return on = function() {
                return n
            }
            ,
            n
        }
        function sn() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  justify-content: center;\n  align-items: center;\n  column-gap: 12px;\n  padding: 16px 19px 20px 19px;\n  height: 106px;\n\n  > img {\n    width: 64px;\n    height: 64px;\n  }\n\n  > div {\n    display: flex;\n    flex-direction: column;\n    row-gap: 6px;\n\n    &.no-record {\n      font-size: 12px;\n      line-height: 12px;\n      color: #808080;\n    }\n\n    > div {\n      display: flex;\n      font-size: 12px;\n      font-weight: 600;\n      line-height: 12px;\n      gap: 4px;\n\n      > b {\n        font-weight: 600;\n        color: #646464;\n      }\n\n      > span {\n        color: #808080;\n      }\n    }\n  }\n"]);
            return sn = function() {
                return n
            }
            ,
            n
        }
        function cn() {
            var n = (0,
            a.Z)(["\n  padding: 15px 19px;\n  border-top: 1px solid #e6e6e6;\n  border-bottom: ", ";\n  display: grid;\n  gap: 12px;\n  grid-template-columns: 1fr 1fr 1fr;\n\n  ", " {\n    grid-template-columns: 1fr 1fr 1fr 1fr 1fr;\n  }\n\n  ", " {\n    grid-template-columns: 1fr 1fr 1fr;\n  }\n"]);
            return cn = function() {
                return n
            }
            ,
            n
        }
        var dn = function(n) {
            var e, t = n.hideBottom, a = (0,
            l.$G)("player").t, o = (0,
            g.Z)(), s = o.name, c = o.isNormalSeason, d = o.isLegacySeason, p = (0,
            v.f)(s).data, x = (0,
            m.dN)().data, h = b.AN.COBALT, f = b.Vo.COBALT, u = (0,
            r.useMemo)((function() {
                var n;
                if (p) {
                    var e = null === (n = p.playerSeasonOverviews) || void 0 === n ? void 0 : n.find((function(n) {
                        return n.matchingModeId === h && n.teamModeId === f
                    }
                    ));
                    return e
                }
            }
            ), [p, h, f]), j = (0,
            r.useMemo)((function() {
                return u ? u.recentMatches.map((function(n) {
                    return {
                        rank: n.gameRank
                    }
                }
                )) : []
            }
            ), [u]), y = w(u), C = y.formatStats, Z = y.percents, M = null === (e = null === x || void 0 === x ? void 0 : x.seasons.find((function(n) {
                return n.key === (null === p || void 0 === p ? void 0 : p.meta.season)
            }
            ))) || void 0 === e ? void 0 : e.name, R = void 0 !== u;
            return (0,
            i.jsxs)(pn, {
                hasOverview: R,
                children: [(0,
                i.jsx)("header", {
                    children: (0,
                    i.jsxs)("h2", {
                        children: [a("gameMode.cobalt"), (0,
                        i.jsxs)("span", {
                            children: ["(", c ? a("gameMode.total") : M, ")"]
                        })]
                    })
                }), (0,
                i.jsxs)(xn, {
                    children: [(0,
                    i.jsx)("img", {
                        src: "".concat(k.DX, "/common/img-gamemode-cobalt.png"),
                        alt: a("gameMode.cobalt")
                    }), u ? (0,
                    i.jsxs)("div", {
                        children: [(0,
                        i.jsxs)("div", {
                            children: [(0,
                            i.jsx)("b", {
                                children: a("statCategory.plays")
                            }), (0,
                            i.jsx)("span", {
                                children: C.plays
                            })]
                        }), (0,
                        i.jsxs)("div", {
                            children: [(0,
                            i.jsx)("b", {
                                children: a("statCategory.avgDamage")
                            }), (0,
                            i.jsx)("span", {
                                children: C.avgDamageToPlayer
                            })]
                        }), (0,
                        i.jsxs)("div", {
                            children: [(0,
                            i.jsx)("b", {
                                children: a("statCategory.winRate")
                            }), (0,
                            i.jsx)("span", {
                                children: C.winRate
                            })]
                        })]
                    }) : (0,
                    i.jsx)("div", {
                        className: "no-record",
                        children: a("noRecord")
                    })]
                }), (0,
                i.jsxs)(hn, {
                    hideBottom: t,
                    children: [(0,
                    i.jsx)(N, {
                        percent: Z.plays,
                        title: a("statCategory.plays"),
                        value: C.plays
                    }), (0,
                    i.jsx)(N, {
                        percent: Z.winRate,
                        title: a("statCategory.winRate"),
                        value: C.winRate,
                        color: "green"
                    }), (0,
                    i.jsx)(N, {
                        percent: Z.avgDamageToPlayer,
                        title: a("statCategory.avgDamage"),
                        value: C.avgDamageToPlayer
                    }), (0,
                    i.jsx)(N, {
                        percent: Z.wins,
                        title: a("statCategory.wins"),
                        value: C.wins
                    }), (0,
                    i.jsx)(N, {
                        percent: Z.avgKill,
                        title: a("statCategory.avgKills"),
                        value: C.avgKill
                    }), (0,
                    i.jsx)(N, {
                        percent: Z.avgDamageToAnimal,
                        title: a("statCategory.avgAnimalDamage"),
                        value: C.avgDamageToAnimal
                    }), (0,
                    i.jsx)(N, {
                        percent: Z.defeats,
                        title: a("statCategory.defeat"),
                        value: C.defeats
                    }), (0,
                    i.jsx)(N, {
                        percent: Z.avgAssist,
                        title: a("statCategory.avgAssi"),
                        value: C.avgAssist
                    }), (0,
                    i.jsx)(N, {
                        percent: Z.avgAnimalKill,
                        title: a("statCategory.avgAnimalKills"),
                        value: C.avgAnimalKill
                    })]
                }), !c && !t && (0,
                i.jsx)("div", {
                    className: "recent-match-wrapper",
                    children: (0,
                    i.jsx)(W, {
                        matches: j,
                        isCobalt: !0
                    })
                }), !c && !d && (0,
                i.jsx)(F(), {
                    href: "/players/".concat(s, "?season=NORMAL&gameMode=COBALT"),
                    children: (0,
                    i.jsx)("a", {
                        className: "total-stat-link",
                        children: a("viewTotalStatistics")
                    })
                }), c && (0,
                i.jsx)(F(), {
                    href: "/players/".concat(s, "?gameMode=COBALT"),
                    children: (0,
                    i.jsx)("a", {
                        className: "total-stat-link recent",
                        children: a("viewRecentStatistics")
                    })
                })]
            })
        }
          , pn = s.Z.section(on())
          , xn = s.Z.div(sn())
          , hn = s.Z.div(cn(), (function(n) {
            return n.hideBottom ? "none" : "1px solid #e6e6e6"
        }
        ), f.B2.md, f.B2.lg)
          , fn = t(84849);
        t(34714);
        function un() {
            var n = (0,
            a.Z)(["\n  width: 100%;\n\n  &:nth-of-type(1),\n  &:nth-of-type(2) {\n    display: none;\n  }\n\n  ", " {\n    &:nth-of-type(1),\n    &:nth-of-type(2) {\n      display: block;\n    }\n  }\n"]);
            return un = function() {
                return n
            }
            ,
            n
        }
        var gn = function() {
            return (0,
            i.jsx)(mn, {
                children: (0,
                i.jsx)(fn.Z, {
                    height: 496
                })
            })
        }
          , mn = s.Z.section(un(), f.B2.xl);
        function vn() {
            var n = (0,
            a.Z)(["\n  border: 1px solid #e6e6e6;\n  background: #ffffff;\n\n  > header {\n    padding: 14px 0px 14px;\n    border-bottom: 1px solid #e6e6e6;\n\n    > h2 {\n      display: flex;\n      align-items: center;\n      justify-content: center;\n      gap: 2px;\n\n      font-size: 14px;\n      font-weight: 600;\n      line-height: 14px;\n      color: #646464;\n      text-align: center;\n\n      > span {\n        font-size: 12px;\n        font-weight: 400;\n        line-height: 12px;\n        color: #808080;\n      }\n    }\n  }\n\n  > .recent-match-wrapper {\n    height: 169px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    padding: 0px 17px;\n  }\n"]);
            return vn = function() {
                return n
            }
            ,
            n
        }
        function jn() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  justify-content: center;\n  align-items: center;\n  column-gap: 12px;\n  height: 106px;\n  font-size: 18px;\n  color: #646464;\n"]);
            return jn = function() {
                return n
            }
            ,
            n
        }
        function yn() {
            var n = (0,
            a.Z)(["\n  padding: 15px 19px;\n  border-top: 1px solid #e6e6e6;\n  border-bottom: 1px solid #e6e6e6;\n  display: grid;\n  gap: 12px;\n  grid-template-columns: 1fr 1fr;\n\n  ", " {\n    grid-template-columns: 1fr 1fr 1fr 1fr;\n  }\n\n  ", " {\n    grid-template-columns: 1fr 1fr;\n  }\n"]);
            return yn = function() {
                return n
            }
            ,
            n
        }
        var wn = function(n) {
            var e, t = n.teamMode, a = (0,
            l.$G)("player").t, o = (0,
            u.Z)({
                selectedTeamMode: t
            }).legacyOverview, s = (0,
            m.dN)().data, c = (0,
            r.useMemo)((function() {
                return o ? o.recentMatches.map((function(n) {
                    return {
                        rank: n.gameRank
                    }
                }
                )) : []
            }
            ), [o]), d = function() {
                var n, e, t = null === o || void 0 === o ? void 0 : o.characterStats, a = null !== (n = null === t || void 0 === t ? void 0 : t.reduce((function(n, e) {
                    return n + e.play
                }
                ), 0)) && void 0 !== n ? n : 0, i = null !== (e = null === t || void 0 === t ? void 0 : t.reduce((function(n, e) {
                    return n + e.top3
                }
                ), 0)) && void 0 !== e ? e : 0;
                return (0,
                y.og)(i, a)
            }(), p = null === (e = null === s || void 0 === s ? void 0 : s.seasons.find((function(n) {
                return "LEGACY" === n.key
            }
            ))) || void 0 === e ? void 0 : e.name;
            return (0,
            i.jsxs)(bn, {
                children: [(0,
                i.jsx)("header", {
                    children: (0,
                    i.jsxs)("h2", {
                        children: [a("teamMode.".concat(t.toLowerCase())), (0,
                        i.jsxs)("span", {
                            children: ["(", p, ")"]
                        })]
                    })
                }), (0,
                i.jsx)(kn, {
                    children: (0,
                    i.jsx)("div", {
                        className: "no-record",
                        children: a("noScore")
                    })
                }), (0,
                i.jsxs)(Cn, {
                    children: [(0,
                    i.jsx)(N, {
                        percent: o && o.avgPlace > 0 ? 100 : 0,
                        title: a("statCategory.avgRank"),
                        value: (0,
                        y.ZD)((null === o || void 0 === o ? void 0 : o.avgPlace) || 0)
                    }), (0,
                    i.jsx)(N, {
                        percent: o && o.win > 0 ? 100 : 0,
                        title: a("statCategory.top3"),
                        value: d
                    }), (0,
                    i.jsx)(N, {
                        percent: o && o.win > 0 ? 100 : 0,
                        title: a("statCategory.winCount"),
                        value: null === o || void 0 === o ? void 0 : o.win
                    }), (0,
                    i.jsx)(N, {
                        percent: o && o.avgPlayerKill > 0 ? 100 : 0,
                        title: a("statCategory.avgKills"),
                        value: null === o || void 0 === o ? void 0 : o.avgPlayerKill
                    })]
                }), (0,
                i.jsx)("div", {
                    className: "recent-match-wrapper",
                    children: (0,
                    i.jsx)(W, {
                        matches: c
                    })
                })]
            })
        }
          , bn = s.Z.section(vn())
          , kn = s.Z.div(jn())
          , Cn = s.Z.div(yn(), f.B2.md, f.B2.lg);
        function Nn() {
            var n = (0,
            a.Z)([""]);
            return Nn = function() {
                return n
            }
            ,
            n
        }
        function Zn() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  flex-direction: column;\n  gap: 12px;\n\n  > section {\n    display: none;\n    border-top: 0px;\n\n    > header {\n      display: none;\n    }\n\n    &:nth-of-type(", ") {\n      display: unset;\n    }\n  }\n\n  ", " {\n    flex-direction: row;\n\n    > section {\n      border-top: 1px solid #e6e6e6;\n      display: block;\n      width: 352.33px;\n\n      > header {\n        display: block;\n      }\n    }\n  }\n"]);
            return Zn = function() {
                return n
            }
            ,
            n
        }
        function Mn() {
            var n = (0,
            a.Z)(["\n  display: flex;\n\n  ", " {\n    display: none;\n  }\n\n  > button {\n    flex: 1;\n    height: 44px;\n    background: #fafafa;\n    font-size: 12px;\n    line-height: 12px;\n    color: #646464;\n    border-bottom: 1px solid #e6e6e6;\n\n    &:not(.active):hover {\n      background: #f5f5f5;\n    }\n\n    &.active {\n      color: #000000;\n      background: #ffffff;\n      border-bottom: none;\n      box-shadow: 0px 2px 0px 0px inset #e09500;\n\n      border-left: 1px solid #e6e6e6;\n      border-right: 1px solid #e6e6e6;\n    }\n  }\n"]);
            return Mn = function() {
                return n
            }
            ,
            n
        }
        var Rn = function(n) {
            var e = n.children
              , t = n.headerTitle
              , a = (0,
            r.useState)(1)
              , l = a[0]
              , o = a[1]
              , s = function(n) {
                return o(n)
            };
            return (0,
            i.jsxs)(An, {
                children: [(0,
                i.jsxs)(Ln, {
                    children: [(0,
                    i.jsx)("button", {
                        onClick: function() {
                            return s(1)
                        },
                        className: d()({
                            active: 1 === l
                        }),
                        children: t[0]
                    }), (0,
                    i.jsx)("button", {
                        onClick: function() {
                            return s(2)
                        },
                        className: d()({
                            active: 2 === l
                        }),
                        children: t[1]
                    }), (0,
                    i.jsx)("button", {
                        onClick: function() {
                            return s(3)
                        },
                        className: d()({
                            active: 3 === l
                        }),
                        children: t[2]
                    })]
                }), (0,
                i.jsx)(Sn, {
                    activeIndex: l,
                    children: e
                })]
            })
        }
          , An = s.Z.div(Nn())
          , Sn = s.Z.div(Zn(), (function(n) {
            return n.activeIndex
        }
        ), f.B2.xl)
          , Ln = s.Z.div(Mn(), f.B2.xl);
        function Dn() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  flex-direction: column;\n  gap: 12px;\n  margin: 20px 0px 32px 0px;\n\n  > section {\n    flex: 1;\n  }\n\n  ", " {\n    flex-direction: row;\n\n    > section {\n      flex: unset;\n      width: 352px;\n    }\n  }\n"]);
            return Dn = function() {
                return n
            }
            ,
            n
        }
        var Bn = function(n) {
            var e = n.isLoading
              , t = (0,
            l.$G)("player").t
              , a = (0,
            g.Z)()
              , r = a.seasonQuery
              , o = a.isNormalSeason
              , s = a.isEarlySeason
              , c = (0,
            u.Z)({}).isLoading;
            return s || "LEGACY" === r ? o ? null : e || c ? (0,
            i.jsxs)(Tn, {
                children: [(0,
                i.jsx)(gn, {}), (0,
                i.jsx)(gn, {}), (0,
                i.jsx)(gn, {})]
            }) : s ? (0,
            i.jsx)(Tn, {
                children: (0,
                i.jsxs)(Rn, {
                    headerTitle: [t("teamMode.solo"), t("teamMode.duo"), t("teamMode.squad")],
                    children: [(0,
                    i.jsx)(E, {
                        teamMode: "SOLO",
                        isEarly: !0
                    }), (0,
                    i.jsx)(E, {
                        teamMode: "DUO",
                        isEarly: !0
                    }), (0,
                    i.jsx)(E, {
                        teamMode: "SQUAD",
                        isEarly: !0
                    })]
                })
            }) : "LEGACY" === r ? (0,
            i.jsx)(Tn, {
                children: (0,
                i.jsxs)(Rn, {
                    headerTitle: [t("teamMode.solo"), t("teamMode.duo"), t("teamMode.squad")],
                    children: [(0,
                    i.jsx)(wn, {
                        teamMode: "SOLO"
                    }), (0,
                    i.jsx)(wn, {
                        teamMode: "DUO"
                    }), (0,
                    i.jsx)(wn, {
                        teamMode: "SQUAD"
                    })]
                })
            }) : (0,
            i.jsx)(Tn, {
                children: (0,
                i.jsxs)(Rn, {
                    headerTitle: [t("gameMode.rank"), t("gameMode.normal"), t("gameMode.cobalt")],
                    children: [(0,
                    i.jsx)(E, {}), (0,
                    i.jsx)(tn, {}), (0,
                    i.jsx)(dn, {})]
                })
            }) : null
        }
          , zn = (0,
        r.memo)(Bn)
          , Tn = s.Z.div(Dn(), f.B2.xl)
          , Kn = t(34009)
          , En = t(26042)
          , _n = t(828)
          , On = t(11163)
          , Pn = t(4480)
          , Gn = t(84968)
          , Fn = t(25683)
          , In = t(52002)
          , $n = t(78239)
          , Un = t(97630);
        function Qn() {
            var n = (0,
            a.Z)(["\n  &:not(.early) {\n    margin-top: 20px;\n  }\n\n  > a {\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    font-size: 12px;\n    font-weight: 600;\n    line-height: 12px;\n    width: 100%;\n    height: 40px;\n    background: #ffffff;\n    color: #36436f;\n    border: 1px solid #d9e3e7;\n    column-gap: 2px;\n  }\n"]);
            return Qn = function() {
                return n
            }
            ,
            n
        }
        function qn() {
            var n = (0,
            a.Z)(["\n  margin-bottom: 8px;\n\n  > table {\n    width: 100%;\n    font-size: 12px;\n    font-weight: 400;\n    line-height: 12px;\n\n    > thead {\n      color: #ffffff;\n      background: #363944;\n      border: 1px solid #363944;\n\n      th {\n        height: 44px;\n        font-weight: 400;\n\n        &.character {\n          text-align: left;\n          padding-left: 16px;\n        }\n        &.win-rate {\n          width: 50px;\n        }\n        &.rp {\n          width: 50px;\n        }\n        &.avg-kill {\n          width: 56px;\n        }\n        &.avg-damage {\n          width: 60px;\n        }\n      }\n    }\n\n    > tbody {\n      border: 1px solid #e6e6e6;\n      border-top: none;\n      border-bottom: none;\n\n      tr {\n        height: 50px;\n        background: #ffffff;\n        border-bottom: 1px solid #e6e6e6;\n      }\n\n      td {\n        color: #646464;\n        font-size: 12px;\n        line-height: 12px;\n        text-align: center;\n\n        &.character {\n          > div {\n            display: flex;\n            align-items: center;\n            padding-left: 8px;\n            column-gap: 8px;\n\n            > .info {\n              flex: 1;\n              display: flex;\n              flex-direction: column;\n              row-gap: 4px;\n              text-align: left;\n              font-size: 12px;\n              line-height: 12px;\n              overflow: hidden;\n\n              > .character-name {\n                color: #000000;\n                overflow: hidden;\n                white-space: nowrap;\n                text-overflow: ellipsis;\n              }\n\n              > .plays {\n                color: #646464;\n              }\n            }\n          }\n        }\n\n        &.avg-kill {\n          > div {\n            width: fit-content;\n            display: flex;\n            flex-direction: column;\n            align-items: center;\n            gap: 4px;\n            margin: 0 auto;\n\n            > div {\n              display: flex;\n              gap: 2px;\n\n              &.kill {\n                background: #f0f0f0;\n                border-radius: 4px;\n                padding: 4px;\n\n                > span {\n                  color: #000000;\n                }\n              }\n\n              > span {\n                font-size: 12px;\n                line-height: 12px;\n\n                &.label {\n                  width: 18px;\n                  font-weight: 600;\n                }\n\n                &.value {\n                  min-width: 24px;\n                  font-weight: 400;\n                  text-align: right;\n                }\n              }\n            }\n          }\n        }\n\n        &.rp {\n          > div {\n            display: flex;\n            gap: 2px;\n            align-items: center;\n            justify-content: center;\n          }\n        }\n\n        &.win-rate {\n          color: #000000;\n        }\n\n        &.no-record {\n          > div {\n            display: flex;\n            align-items: center;\n            justify-content: center;\n            height: 320px;\n            font-size: 12px;\n            line-height: 16px;\n            color: #808080;\n          }\n        }\n      }\n    }\n  }\n"]);
            return qn = function() {
                return n
            }
            ,
            n
        }
        function Vn() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  padding: 12px 16px;\n  background: #4c4f5d;\n\n  > h3 {\n    color: #ffffff;\n    font-size: 12px;\n    font-weight: 400;\n    line-height: 12px;\n\n    > b {\n      font-weight: 600;\n      margin-right: 4px;\n    }\n  }\n"]);
            return Vn = function() {
                return n
            }
            ,
            n
        }
        function Xn() {
            var n = (0,
            a.Z)(["\n  position: relative;\n  width: ", ";\n\n  > .character-image-wrapper {\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    overflow: hidden;\n    width: 36px;\n    height: 36px;\n    border-radius: 18px;\n    object-fit: cover;\n    object-position: center;\n    background: #d6d6d6;\n  }\n\n  > .weapon-image-wrapper {\n    position: absolute;\n    bottom: 0;\n    right: 0px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    overflow: hidden;\n    width: 20px;\n    height: 20px;\n    border-radius: 10px;\n    background: #323232;\n\n    > img {\n      width: 14px;\n      height: 14px;\n      object-fit: contain;\n    }\n  }\n"]);
            return Xn = function() {
                return n
            }
            ,
            n
        }
        function Hn() {
            var n = (0,
            a.Z)(["\n  width: fit-content;\n  display: flex;\n  align-items: center;\n  gap: 6px;\n  cursor: pointer;\n\n  > span {\n    font-size: 12px;\n    line-height: 12px;\n    color: #ffffff;\n  }\n\n  input[type='checkbox'] {\n    -webkit-appearance: none;\n    -moz-appearance: none;\n    appearance: none;\n    background: transparent;\n    border-radius: 4px;\n    width: 16px;\n    height: 16px;\n    outline: 1px solid #848999;\n    margin: 0;\n    cursor: pointer;\n    overflow: hidden;\n  }\n\n  input[type='checkbox']:checked {\n    background: #e09500;\n    outline: 1px solid #e09500;\n    box-shadow: 0 0 0 1px #e09500 inset;\n  }\n\n  input[type='checkbox']:checked::before {\n    background: url(", "/icons/check.svg) no-repeat;\n    background-position: center;\n    position: absolute;\n    content: '';\n    width: 16px;\n    height: 15px;\n  }\n\n  &:hover {\n    input[type='checkbox'] {\n      outline: 1px solid #e09500;\n    }\n  }\n"]);
            return Hn = function() {
                return n
            }
            ,
            n
        }
        var Wn = function() {
            return (0,
            i.jsx)("svg", {
                width: "11",
                height: "10",
                viewBox: "0 0 11 10",
                fill: "none",
                xmlns: "http://www.w3.org/2000/svg",
                children: (0,
                i.jsx)("path", {
                    d: "M4.52363 0.780167L8.4739 4.66445C8.56024 4.76613 8.625 4.88815 8.625 5.01017C8.625 5.13219 8.56024 5.25421 8.4739 5.33555L4.52363 9.21983C4.32935 9.4232 3.98398 9.4232 3.7897 9.24017C3.57384 9.05714 3.57384 8.75209 3.76811 8.54873L7.39459 4.98983L3.76811 1.45127C3.57384 1.26824 3.57384 0.942859 3.7897 0.75983C3.98398 0.576801 4.32935 0.576801 4.52363 0.780167Z",
                    fill: "#36436F"
                })
            })
        }
          , Yn = function(n) {
            var e = n.isEarly
              , t = (0,
            l.$G)("player").t
              , a = (0,
            On.useRouter)().query
              , r = (0,
            g.Z)()
              , o = r.gameModeQuery
              , s = r.name
              , c = r.isNormalSeason
              , p = (0,
            $n.v)().getCharacterImageURL
              , x = (0,
            _n.Z)((0,
            Pn.FV)(Fn.y8), 2)
              , h = x[0]
              , f = x[1]
              , m = (0,
            u.Z)({
                selectedGameMode: "ALL" === o ? "RANK" : o
            })
              , v = m.characterStats
              , j = m.hasWeaponStats
              , w = (0,
            In.Z)()
              , b = w.getCharacterByKey
              , C = w.getMasteryByKey
              , N = "ALL" === o || "RANK" === o
              , Z = (0,
            En.Z)({}, a);
            return delete Z.name,
            (0,
            i.jsxs)(Jn, {
                className: d()({
                    early: e
                }),
                children: [(0,
                i.jsxs)(ne, {
                    children: [(0,
                    i.jsxs)(ee, {
                        children: [(0,
                        i.jsxs)("h3", {
                            children: [c && (0,
                            i.jsx)("b", {
                                children: t("NORMAL" === o ? "gameMode.normal" : "gameMode.cobalt")
                            }), !c && (0,
                            i.jsx)("b", {
                                children: t("ALL" === o ? "gameMode.rank" : "gameMode.".concat(o.toLowerCase()))
                            }), t("characterListTitle")]
                        }), j && (0,
                        i.jsxs)(ae, {
                            onClick: function() {
                                return f((function(n) {
                                    return !n
                                }
                                ))
                            },
                            children: [(0,
                            i.jsx)("input", {
                                type: "checkbox",
                                readOnly: !0,
                                checked: h
                            }), (0,
                            i.jsx)("span", {
                                children: t("statisticsByWeapon")
                            })]
                        })]
                    }), (0,
                    i.jsxs)("table", {
                        children: [(0,
                        i.jsx)("thead", {
                            children: (0,
                            i.jsxs)("tr", {
                                children: [(0,
                                i.jsx)("th", {
                                    className: "character",
                                    children: t("character")
                                }), (0,
                                i.jsx)("th", {
                                    className: "win-rate",
                                    children: t("statCategory.winRate")
                                }), N && (0,
                                i.jsx)("th", {
                                    className: "rp",
                                    children: t("statCategory.rp")
                                }), (0,
                                i.jsx)("th", {
                                    className: "avg-kill",
                                    children: t("statCategory.avgKills")
                                }), (0,
                                i.jsx)("th", {
                                    className: "avg-damage",
                                    children: t("statCategory.avgDmg")
                                })]
                            })
                        }), (0,
                        i.jsx)("tbody", {
                            children: (null === v || void 0 === v ? void 0 : v.length) > 0 ? v.slice(0, 10).map((function(n, e) {
                                var a = b(n.key)
                                  , r = n.weaponKey ? C(n.weaponKey) : void 0;
                                return (0,
                                i.jsxs)("tr", {
                                    children: [(0,
                                    i.jsx)("td", {
                                        className: "character",
                                        children: (0,
                                        i.jsxs)("div", {
                                            children: [(0,
                                            i.jsxs)(te, {
                                                $showWeapon: void 0 !== r && h,
                                                children: [(0,
                                                i.jsx)(F(), {
                                                    href: "/characters/".concat(null === a || void 0 === a ? void 0 : a.key).concat(r ? "?weaponType=".concat(r.key) : ""),
                                                    children: (0,
                                                    i.jsx)("a", {
                                                        className: "character-image-wrapper",
                                                        target: "_blank",
                                                        children: (0,
                                                        i.jsx)("img", {
                                                            src: p(null === a || void 0 === a ? void 0 : a.imageName),
                                                            alt: null === a || void 0 === a ? void 0 : a.name
                                                        })
                                                    })
                                                }), r && (0,
                                                i.jsx)(Gn.Z, {
                                                    overlay: r.name,
                                                    placement: "top",
                                                    children: (0,
                                                    i.jsx)("div", {
                                                        className: "weapon-image-wrapper",
                                                        children: (0,
                                                        i.jsx)("img", {
                                                            src: r.iconUrl,
                                                            alt: r.name
                                                        })
                                                    })
                                                })]
                                            }), (0,
                                            i.jsxs)("div", {
                                                className: "info",
                                                children: [(0,
                                                i.jsx)("div", {
                                                    className: "character-name",
                                                    children: null === a || void 0 === a ? void 0 : a.name
                                                }), (0,
                                                i.jsxs)("div", {
                                                    className: "plays",
                                                    children: [n.play, " ", t("statCategory.game")]
                                                })]
                                            })]
                                        })
                                    }), (0,
                                    i.jsx)("td", {
                                        className: "win-rate",
                                        children: (0,
                                        y.og)(n.win, n.play)
                                    }), N && (0,
                                    i.jsx)("td", {
                                        className: "rp",
                                        children: (0,
                                        i.jsxs)("div", {
                                            children: [+n.mmrGain > 0 && (0,
                                            i.jsx)("img", {
                                                src: "".concat(k.DX, "/icons/arrow-up.svg"),
                                                alt: "up-arrow",
                                                width: 8
                                            }), +n.mmrGain < 0 && (0,
                                            i.jsx)("img", {
                                                src: "".concat(k.DX, "/icons/arrow-down.svg"),
                                                alt: "down-arrow",
                                                width: 8
                                            }), Math.abs(n.mmrGain)]
                                        })
                                    }), (0,
                                    i.jsx)("td", {
                                        className: "avg-kill",
                                        children: (0,
                                        i.jsxs)("div", {
                                            children: [(0,
                                            i.jsxs)("div", {
                                                className: "team-kill",
                                                children: [(0,
                                                i.jsx)("span", {
                                                    className: "label",
                                                    children: "TK"
                                                }), (0,
                                                i.jsx)("span", {
                                                    className: "value",
                                                    children: (0,
                                                    y.RD)(n.teamKill / n.play)
                                                })]
                                            }), (0,
                                            i.jsxs)("div", {
                                                className: "kill",
                                                children: [(0,
                                                i.jsx)("span", {
                                                    className: "label",
                                                    children: "K"
                                                }), (0,
                                                i.jsx)("span", {
                                                    className: "value",
                                                    children: (0,
                                                    y.RD)(n.playerKill / n.play)
                                                })]
                                            })]
                                        })
                                    }), (0,
                                    i.jsx)("td", {
                                        className: "avg-damage",
                                        children: (0,
                                        y.JG)(n.damageToPlayer / n.play)
                                    })]
                                }, e)
                            }
                            )) : (0,
                            i.jsx)("tr", {
                                children: (0,
                                i.jsx)("td", {
                                    className: "no-record",
                                    colSpan: N ? 5 : 4,
                                    children: (0,
                                    i.jsx)(Un.Z, {
                                        type: "noRecord"
                                    })
                                })
                            })
                        })]
                    })]
                }), (0,
                i.jsx)(F(), {
                    href: {
                        pathname: "/players/".concat(s, "/character/"),
                        query: Z
                    },
                    shallow: !0,
                    children: (0,
                    i.jsxs)("a", {
                        children: [(0,
                        i.jsx)("span", {
                            children: t("moreCharacterStats")
                        }), (0,
                        i.jsx)(Wn, {})]
                    })
                })]
            })
        }
          , Jn = s.Z.div(Qn())
          , ne = s.Z.section(qn())
          , ee = s.Z.div(Vn())
          , te = s.Z.div(Xn(), (function(n) {
            return n.$showWeapon ? "48px" : "36px"
        }
        ))
          , ae = s.Z.div(Hn(), k.DX);
        function ie() {
            var n = (0,
            a.Z)(["\n  margin-top: 20px;\n\n  > a {\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    font-size: 12px;\n    font-weight: 600;\n    line-height: 12px;\n    width: 100%;\n    height: 40px;\n    background: #ffffff;\n    color: #36436f;\n    border: 1px solid #d9e3e7;\n    column-gap: 2px;\n  }\n"]);
            return ie = function() {
                return n
            }
            ,
            n
        }
        function re() {
            var n = (0,
            a.Z)(["\n  > table {\n    width: 100%;\n    font-size: 12px;\n    font-weight: 400;\n    line-height: 12px;\n\n    > thead {\n      color: #ffffff;\n      background: #363944;\n      border: 1px solid #363944;\n\n      th {\n        height: 44px;\n        font-weight: 400;\n\n        &.character {\n          text-align: left;\n          padding-left: 16px;\n        }\n        &.win-rate {\n          width: 56px;\n        }\n        &.avg-rank {\n          width: 60px;\n        }\n      }\n    }\n\n    > tbody {\n      border: 1px solid #e6e6e6;\n      border-top: none;\n      border-bottom: none;\n\n      tr {\n        height: 50px;\n        background: #ffffff;\n        border-bottom: 1px solid #e6e6e6;\n      }\n\n      td {\n        color: #646464;\n        font-size: 12px;\n        line-height: 12px;\n        text-align: center;\n\n        &.character {\n          > div {\n            display: flex;\n            align-items: center;\n            padding-left: 8px;\n            column-gap: 8px;\n\n            > .image-wrapper {\n              display: flex;\n              align-items: center;\n              justify-content: center;\n              overflow: hidden;\n              width: 36px;\n              height: 36px;\n              border-radius: 18px;\n              object-fit: cover;\n              object-position: center;\n              background: #d6d6d6;\n            }\n\n            > .info {\n              display: flex;\n              flex-direction: column;\n              row-gap: 4px;\n              text-align: left;\n              font-size: 12px;\n              line-height: 12px;\n\n              > .character-name {\n                color: #000000;\n\n                > a:hover {\n                  text-decoration: underline;\n                  text-underline-offset: 2px;\n                }\n              }\n\n              > .plays {\n                color: #646464;\n              }\n            }\n          }\n        }\n\n        &.win-rate {\n          color: #000000;\n        }\n\n        &.no-record {\n          > div {\n            display: flex;\n            align-items: center;\n            justify-content: center;\n            height: 180px;\n            font-size: 12px;\n            line-height: 16px;\n            color: #808080;\n          }\n        }\n      }\n    }\n  }\n"]);
            return re = function() {
                return n
            }
            ,
            n
        }
        var le = function() {
            var n = (0,
            l.$G)("player").t
              , e = (0,
            u.Z)({}).overview
              , t = (0,
            In.Z)().getCharacterByKey
              , a = (0,
            $n.v)().getCharacterImageURL
              , o = (0,
            r.useMemo)((function() {
                if (!e)
                    return !1;
                var n = e.userNum;
                return !(e.seasonId < 31) || 3606803 !== n && 3989935 !== n
            }
            ), [e]);
            return (0,
            i.jsx)(oe, {
                children: (0,
                i.jsx)(se, {
                    children: (0,
                    i.jsxs)("table", {
                        children: [(0,
                        i.jsx)("thead", {
                            children: (0,
                            i.jsxs)("tr", {
                                children: [(0,
                                i.jsx)("th", {
                                    className: "character",
                                    children: n("duoStats")
                                }), (0,
                                i.jsx)("th", {
                                    className: "win-rate",
                                    children: n("statCategory.winRate")
                                }), (0,
                                i.jsx)("th", {
                                    className: "avg-rank",
                                    children: n("statCategory.avgRank")
                                })]
                            })
                        }), (0,
                        i.jsx)("tbody", {
                            children: o && e && e.duoStats.length > 0 ? e.duoStats.map((function(e, r) {
                                var l, o = t(null === (l = e.characterStats[0]) || void 0 === l ? void 0 : l.key);
                                return (0,
                                i.jsxs)("tr", {
                                    children: [(0,
                                    i.jsx)("td", {
                                        className: "character",
                                        children: (0,
                                        i.jsxs)("div", {
                                            children: [(0,
                                            i.jsx)(F(), {
                                                href: "/characters/".concat(null === o || void 0 === o ? void 0 : o.key),
                                                children: (0,
                                                i.jsx)("a", {
                                                    className: "image-wrapper",
                                                    target: "_blank",
                                                    children: (0,
                                                    i.jsx)("img", {
                                                        src: a(null === o || void 0 === o ? void 0 : o.imageName),
                                                        alt: null === o || void 0 === o ? void 0 : o.name
                                                    })
                                                })
                                            }), (0,
                                            i.jsxs)("div", {
                                                className: "info",
                                                children: [(0,
                                                i.jsx)("div", {
                                                    className: "character-name",
                                                    children: (0,
                                                    i.jsx)(F(), {
                                                        href: "/players/".concat(e.nickname),
                                                        children: (0,
                                                        i.jsx)("a", {
                                                            target: "_blank",
                                                            children: e.nickname
                                                        })
                                                    })
                                                }), (0,
                                                i.jsxs)("div", {
                                                    className: "plays",
                                                    children: [e.play, " ", n("statCategory.game")]
                                                })]
                                            })]
                                        })
                                    }), (0,
                                    i.jsx)("td", {
                                        className: "win-rate",
                                        children: (0,
                                        y._f)(e.win, e.play)
                                    }), (0,
                                    i.jsx)("td", {
                                        className: "avg-rank",
                                        children: (0,
                                        y.ZD)(e.place / e.play)
                                    })]
                                }, r)
                            }
                            )) : (0,
                            i.jsx)("tr", {
                                children: (0,
                                i.jsx)("td", {
                                    className: "no-record",
                                    colSpan: 3,
                                    children: (0,
                                    i.jsx)(Un.Z, {
                                        type: "noRecord"
                                    })
                                })
                            })
                        })]
                    })
                })
            })
        }
          , oe = s.Z.div(ie())
          , se = s.Z.section(re());
        function ce() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  align-items: center;\n  flex-direction: column;\n  row-gap: 6px;\n  font-size: 12px;\n  line-height: 12px;\n  width: 100%;\n\n  > .match-item-wrapper {\n    width: 324px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    gap: 4px;\n    flex-wrap: wrap;\n\n    ", " {\n      width: 100%;\n    }\n  }\n"]);
            return ce = function() {
                return n
            }
            ,
            n
        }
        var de = function(n) {
            var e = n.matches
              , t = "COBALT" === (0,
            g.Z)().gameModeQuery
              , a = Array.from({
                length: 20 - e.length
            });
            return (0,
            i.jsx)(pe, {
                children: (0,
                i.jsxs)("div", {
                    className: "match-item-wrapper",
                    children: [e.map((function(n, e) {
                        return (0,
                        i.jsx)(q, {
                            rank: n.gameRank,
                            isEscape: 3 === n.escapeState,
                            isCobalt: t
                        }, e)
                    }
                    )), a.map((function(n, e) {
                        return (0,
                        i.jsx)(q, {
                            isNull: !0
                        }, e)
                    }
                    ))]
                })
            })
        }
          , pe = s.Z.div(ce(), f.B2.md)
          , xe = t(75490);
        function he() {
            var n = (0,
            a.Z)(["\n  border: 1px solid #e6e6e6;\n  background: #ffffff;\n\n  ", " {\n    flex-direction: row;\n    grid-template-columns: 1fr 1fr 1fr;\n  }\n\n  > .top {\n    height: 44px;\n    border-bottom: 1px solid #e6e6e6;\n    padding: 5px 5px 5px 15px;\n    display: flex;\n    justify-content: space-between;\n    align-items: center;\n    column-gap: 4px;\n\n    > h3 {\n      font-size: 12px;\n      font-weight: 600;\n      line-height: 12px;\n      color: #646464;\n\n      > span {\n        font-weight: 400;\n      }\n    }\n  }\n\n  > div {\n    padding: 24px 0px 20px 0px;\n  }\n"]);
            return he = function() {
                return n
            }
            ,
            n
        }
        function fe() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  justify-content: center;\n  align-items: center;\n  column-gap: 24px;\n  margin-bottom: 20px;\n\n  > .bar {\n    width: 1px;\n    height: 16px;\n    background: #e6e6e6;\n  }\n\n  > .info {\n    display: flex;\n    flex-direction: column;\n    align-items: center;\n    row-gap: 8px;\n    color: #808080;\n\n    > .title {\n      font-size: 12px;\n      line-height: 12px;\n    }\n\n    > .value {\n      font-size: 16px;\n      font-weight: 600;\n      line-height: 16px;\n\n      &.green {\n        color: #11b288;\n      }\n\n      &.blue {\n        color: #207ac7;\n      }\n    }\n  }\n"]);
            return fe = function() {
                return n
            }
            ,
            n
        }
        var ue = function() {
            var n, e = (0,
            l.$G)("player").t, t = (0,
            g.Z)(), a = t.gameModeQuery, o = t.isNormalSeason, s = t.characterQuery, c = (0,
            u.Z)({
                selectedGameMode: "ALL" === a ? "RANK" : a
            }).legacyOverview, d = (0,
            v.lp)("ALL" === a ? "RANK" : a, s).data, p = (0,
            r.useMemo)((function() {
                return c ? c.recentMatches : d ? null === d || void 0 === d ? void 0 : d.matches : []
            }
            ), [d, c]), x = "COBALT" === a, h = p.reduce((function(n, e) {
                return n + e.gameRank
            }
            ), 0) / (p.length || 1), f = (0,
            y.ZD)(h), m = p.filter((function(n) {
                return 1 === n.gameRank
            }
            )).length, j = p.filter((function(n) {
                return 2 === n.gameRank
            }
            )).length, w = p.filter((function(n) {
                return n.gameRank <= 3
            }
            )).length, b = p.reduce((function(e, t) {
                return e + (null !== (n = t.teamKill) && void 0 !== n ? n : 0)
            }
            ), 0) / (p.length || 1), k = (0,
            I.isNumber)(m) && m > 0 ? (m / (p.length || 1) * 100).toFixed(1) : 0, C = 0 === h ? "" : h <= 1.99 ? "green" : h <= 3.99 ? "blue" : "";
            return (0,
            i.jsxs)(ge, {
                children: [(0,
                i.jsxs)("div", {
                    className: "top",
                    children: [(0,
                    i.jsxs)("h3", {
                        children: [e("recentMatchesSummary"), "ALL" === a ? (0,
                        i.jsxs)("span", {
                            children: ["(", e(o ? "gameMode.normal" : "gameMode.rank"), ")"]
                        }) : (0,
                        i.jsxs)("span", {
                            children: ["(", e("gameMode.".concat(a.toLowerCase())), ")"]
                        })]
                    }), (0,
                    i.jsx)(xe.Z, {})]
                }), (0,
                i.jsxs)("div", {
                    children: [(0,
                    i.jsxs)(me, {
                        children: [x ? (0,
                        i.jsxs)("div", {
                            className: "info",
                            children: [(0,
                            i.jsx)("div", {
                                className: "title",
                                children: e("statCategory.winRate")
                            }), (0,
                            i.jsxs)("div", {
                                className: "value green",
                                children: [k, "%"]
                            })]
                        }) : (0,
                        i.jsxs)("div", {
                            className: "info",
                            children: [(0,
                            i.jsx)("div", {
                                className: "title",
                                children: e("statCategory.avgRank")
                            }), (0,
                            i.jsx)("div", {
                                className: "value ".concat(C),
                                children: f
                            })]
                        }), (0,
                        i.jsx)("div", {
                            className: "bar"
                        }), (0,
                        i.jsxs)("div", {
                            className: "info",
                            children: [(0,
                            i.jsx)("div", {
                                className: "title",
                                children: e("statCategory.winCount")
                            }), (0,
                            i.jsx)("div", {
                                className: "value green",
                                children: m
                            })]
                        }), (0,
                        i.jsx)("div", {
                            className: "bar"
                        }), x ? (0,
                        i.jsxs)("div", {
                            className: "info",
                            children: [(0,
                            i.jsx)("div", {
                                className: "title",
                                children: e("statCategory.loses")
                            }), (0,
                            i.jsx)("div", {
                                className: "value",
                                children: j
                            })]
                        }) : (0,
                        i.jsxs)("div", {
                            className: "info",
                            children: [(0,
                            i.jsx)("div", {
                                className: "title",
                                children: e("statCategory.top3")
                            }), (0,
                            i.jsx)("div", {
                                className: "value",
                                children: w
                            })]
                        }), (0,
                        i.jsx)("div", {
                            className: "bar"
                        }), (0,
                        i.jsxs)("div", {
                            className: "info",
                            children: [(0,
                            i.jsx)("div", {
                                className: "title",
                                children: e("statCategory.avgTeamKill")
                            }), (0,
                            i.jsx)("div", {
                                className: "value",
                                children: b.toFixed(2)
                            })]
                        })]
                    }), (0,
                    i.jsx)(de, {
                        matches: p
                    })]
                })]
            })
        }
          , ge = s.Z.section(he(), f.B2.lg)
          , me = s.Z.div(fe())
          , ve = t(69396)
          , je = t(55986)
          , ye = t(90434)
          , we = t(80207);
        function be() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  flex-direction: column;\n  gap: 4px;\n\n  > .no-record {\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    font-size: 14px;\n    color: #808080;\n    gap: 4px;\n    border: 1px solid #e6e6e6;\n    background: #ffffff;\n    height: 80px;\n  }\n\n  > a {\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    font-size: 12px;\n    font-weight: 600;\n    line-height: 12px;\n    gap: 2px;\n    color: #36436f;\n    background: #ffffff;\n    width: 100%;\n    height: 40px;\n    border: 1px solid #d9e3e7;\n\n    &:hover {\n      background: #fafafa;\n    }\n  }\n"]);
            return be = function() {
                return n
            }
            ,
            n
        }
        var ke = function() {
            return (0,
            i.jsxs)("svg", {
                width: "10",
                height: "10",
                viewBox: "0 0 10 10",
                fill: "none",
                xmlns: "http://www.w3.org/2000/svg",
                children: [(0,
                i.jsx)("g", {
                    clipPath: "url(#clip0_1602_25198)",
                    children: (0,
                    i.jsx)("path", {
                        d: "M11 4.97115C11 5.375 10.6827 5.66346 10.3077 5.66346H5.69231V10.2788C5.69231 10.6827 5.375 11 5 11C4.59615 11 4.30769 10.6827 4.30769 10.2788V5.66346H-0.307692C-0.711538 5.66346 -1 5.375 -1 5C-1 4.59615 -0.711538 4.27885 -0.307692 4.27885H4.30769V-0.336538C4.30769 -0.711538 4.59615 -1 5 -1C5.375 -1 5.69231 -0.711538 5.69231 -0.336538V4.27885H10.3077C10.6827 4.27885 11 4.59615 11 4.97115Z",
                        fill: "#36436F"
                    })
                }), (0,
                i.jsx)("defs", {
                    children: (0,
                    i.jsx)("clipPath", {
                        id: "clip0_1602_25198",
                        children: (0,
                        i.jsx)("rect", {
                            width: "10",
                            height: "10",
                            fill: "white"
                        })
                    })
                })]
            })
        }
          , Ce = function() {
            var n = (0,
            On.useRouter)()
              , e = (0,
            l.$G)("player").t
              , t = (0,
            g.Z)()
              , a = t.name
              , o = t.seasonQuery
              , s = t.characterQuery
              , c = (0,
            v.lp)(void 0, s).data
              , d = (0,
            u.Z)({}).legacyOverview
              , p = (0,
            r.useMemo)((function() {
                return c && c.matches.length > 0 ? c.matches : []
            }
            ), [c]);
            if (!c && !d)
                return null;
            var x = "LEGACY" === o
              , h = (0,
            En.Z)({}, n.query);
            return delete h.name,
            x ? (0,
            i.jsxs)(Ne, {
                children: [d && (null === d || void 0 === d ? void 0 : d.recentMatches.length) > 0 ? null === d || void 0 === d ? void 0 : d.recentMatches.map((function(n, e) {
                    return (0,
                    i.jsx)(we.Z, {
                        match: n
                    }, e)
                }
                )) : (0,
                i.jsxs)("p", {
                    className: "no-record",
                    children: [(0,
                    i.jsx)(je.Z, {
                        size: 14,
                        fill: "#808080"
                    }), e("yetData")]
                }), d && (null === d || void 0 === d ? void 0 : d.recentMatches.length) > 20 && (0,
                i.jsx)(F(), {
                    href: {
                        pathname: "/players/".concat(a, "/matches"),
                        query: (0,
                        ve.Z)((0,
                        En.Z)({}, h), {
                            page: 2
                        })
                    },
                    children: (0,
                    i.jsxs)("a", {
                        children: [(0,
                        i.jsx)(ke, {}), e("seeMore")]
                    })
                })]
            }) : (0,
            i.jsxs)(Ne, {
                children: [p.length > 0 ? p.map((function(n, e) {
                    return (0,
                    i.jsx)(ye.Z, {
                        show970Banner: !1,
                        index: e,
                        match: n
                    }, n.gameId)
                }
                )) : (0,
                i.jsxs)("p", {
                    className: "no-record",
                    children: [(0,
                    i.jsx)(je.Z, {
                        size: 14,
                        fill: "#808080"
                    }), e("yetData")]
                }), c && c.meta.count > 20 && (0,
                i.jsx)(F(), {
                    href: {
                        pathname: "/players/".concat(a, "/matches"),
                        query: (0,
                        ve.Z)((0,
                        En.Z)({}, h), {
                            page: 2
                        })
                    },
                    children: (0,
                    i.jsxs)("a", {
                        children: [(0,
                        i.jsx)(ke, {}), e("seeMore")]
                    })
                })]
            })
        }
          , Ne = s.Z.section(be())
          , Ze = t(63749);
        function Me() {
            var n = (0,
            a.Z)(["\n  width: 100%;\n\n  > .content-wrapper {\n    display: flex;\n    flex-direction: column;\n    row-gap: 20px;\n    column-gap: 12px;\n\n    ", " {\n      flex-direction: row;\n    }\n\n    > .left {\n      display: flex;\n      flex-direction: column;\n      row-gap: 20px;\n      width: 100%;\n\n      ", " {\n        width: 352px;\n      }\n\n      .stat-table {\n        width: 100%;\n        height: 580px;\n      }\n\n      .play-together-table {\n        width: 100%;\n        height: 294px;\n      }\n    }\n\n    > .right {\n      flex: 1;\n      display: flex;\n      flex-direction: column;\n      row-gap: 8px;\n\n      > .matches {\n        display: flex;\n        flex-direction: column;\n        row-gap: 4px;\n      }\n\n      > .recent-match-summary {\n        height: 204px;\n\n        ", " {\n          height: 172px;\n        }\n      }\n    }\n  }\n"]);
            return Me = function() {
                return n
            }
            ,
            n
        }
        var Re = function() {
            return (0,
            i.jsx)(Ae, {
                children: (0,
                i.jsxs)("div", {
                    className: "content-wrapper",
                    children: [(0,
                    i.jsxs)("div", {
                        className: "left",
                        children: [(0,
                        i.jsx)("div", {
                            className: "stat-table",
                            children: (0,
                            i.jsx)(fn.Z, {
                                height: "100%"
                            })
                        }), (0,
                        i.jsx)("div", {
                            className: "play-together-table",
                            children: (0,
                            i.jsx)(fn.Z, {
                                height: "100%"
                            })
                        })]
                    }), (0,
                    i.jsxs)("div", {
                        className: "right",
                        children: [(0,
                        i.jsx)("div", {
                            className: "recent-match-summary",
                            children: (0,
                            i.jsx)(fn.Z, {
                                height: "100%"
                            })
                        }), (0,
                        i.jsx)("div", {
                            className: "matches",
                            children: (0,
                            i.jsx)(Ze.Z, {
                                count: 20
                            })
                        })]
                    })]
                })
            })
        }
          , Ae = s.Z.section(Me(), f.B2.xl, f.B2.xl, f.B2.md)
          , Se = t(79760);
        function Le() {
            var n = (0,
            a.Z)(["\n  > a {\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    font-size: 12px;\n    font-weight: 600;\n    line-height: 12px;\n    width: 100%;\n    height: 40px;\n    background: #ffffff;\n    color: #36436f;\n    border: 1px solid #d9e3e7;\n    column-gap: 2px;\n  }\n"]);
            return Le = function() {
                return n
            }
            ,
            n
        }
        function De() {
            var n = (0,
            a.Z)(["\n  margin-bottom: 8px;\n\n  > h3 {\n    padding: 12px 16px;\n    background: #4c4f5d;\n    color: #ffffff;\n    font-size: 12px;\n    font-weight: 400;\n    line-height: 12px;\n\n    > b {\n      font-weight: 600;\n      margin-right: 4px;\n    }\n  }\n\n  > table {\n    width: 100%;\n    font-size: 12px;\n    font-weight: 400;\n    line-height: 12px;\n\n    > thead {\n      color: #ffffff;\n      background: #363944;\n      border: 1px solid #363944;\n\n      th {\n        height: 44px;\n        font-weight: 400;\n\n        &.character {\n          text-align: left;\n          padding-left: 16px;\n        }\n        &.most-kill,\n        &.avg-rank,\n        &.avg-top3 {\n          width: 56px;\n        }\n      }\n    }\n\n    > tbody {\n      border: 1px solid #e6e6e6;\n      border-top: none;\n      border-bottom: none;\n\n      tr {\n        height: 50px;\n        background: #ffffff;\n        border-bottom: 1px solid #e6e6e6;\n      }\n\n      td {\n        color: #646464;\n        font-size: 12px;\n        line-height: 12px;\n        text-align: center;\n\n        &.character {\n          > div {\n            display: flex;\n            align-items: center;\n            padding-left: 8px;\n            column-gap: 8px;\n\n            > .image-wrapper {\n              display: flex;\n              align-items: center;\n              justify-content: center;\n              overflow: hidden;\n              width: 36px;\n              height: 36px;\n              border-radius: 18px;\n              object-fit: cover;\n              object-position: center;\n              background: #d6d6d6;\n            }\n\n            > .info {\n              display: flex;\n              flex-direction: column;\n              row-gap: 4px;\n              text-align: left;\n              font-size: 12px;\n              line-height: 12px;\n\n              > .character-name {\n                color: #000000;\n              }\n\n              > .plays {\n                color: #646464;\n              }\n            }\n          }\n        }\n\n        &.rp {\n          > div {\n            display: flex;\n            gap: 2px;\n            align-items: center;\n            justify-content: center;\n          }\n        }\n\n        &.no-record {\n          > div {\n            display: flex;\n            align-items: center;\n            justify-content: center;\n            height: 320px;\n            font-size: 12px;\n            line-height: 16px;\n            color: #808080;\n          }\n        }\n      }\n    }\n  }\n"]);
            return De = function() {
                return n
            }
            ,
            n
        }
        var Be = function() {
            return (0,
            i.jsx)("svg", {
                width: "11",
                height: "10",
                viewBox: "0 0 11 10",
                fill: "none",
                xmlns: "http://www.w3.org/2000/svg",
                children: (0,
                i.jsx)("path", {
                    d: "M4.52363 0.780167L8.4739 4.66445C8.56024 4.76613 8.625 4.88815 8.625 5.01017C8.625 5.13219 8.56024 5.25421 8.4739 5.33555L4.52363 9.21983C4.32935 9.4232 3.98398 9.4232 3.7897 9.24017C3.57384 9.05714 3.57384 8.75209 3.76811 8.54873L7.39459 4.98983L3.76811 1.45127C3.57384 1.26824 3.57384 0.942859 3.7897 0.75983C3.98398 0.576801 4.32935 0.576801 4.52363 0.780167Z",
                    fill: "#36436F"
                })
            })
        }
          , ze = function() {
            var n = (0,
            l.$G)("player").t
              , e = (0,
            On.useRouter)().query
              , t = (0,
            g.Z)()
              , a = t.teamModeQuery
              , r = t.name
              , o = (0,
            In.Z)().getCharacterByKey
              , s = (0,
            u.Z)({
                selectedTeamMode: a
            }).legacyOverview
              , c = (0,
            En.Z)({}, e);
            return delete c.name,
            (0,
            i.jsxs)(Te, {
                children: [(0,
                i.jsxs)(Ke, {
                    children: [(0,
                    i.jsxs)("h3", {
                        children: [(0,
                        i.jsx)("b", {
                            children: n("teamMode.".concat(a.toLowerCase()))
                        }), n("characterListTitle")]
                    }), (0,
                    i.jsxs)("table", {
                        children: [(0,
                        i.jsx)("thead", {
                            children: (0,
                            i.jsxs)("tr", {
                                children: [(0,
                                i.jsx)("th", {
                                    className: "character",
                                    children: n("character")
                                }), (0,
                                i.jsx)("th", {
                                    className: "most-kill",
                                    children: n("statCategory.maxPlayerKill")
                                }), (0,
                                i.jsx)("th", {
                                    className: "avg-rank",
                                    children: n("statCategory.avgRank")
                                }), (0,
                                i.jsx)("th", {
                                    className: "avg-top3",
                                    children: n("statCategory.top3")
                                })]
                            })
                        }), (0,
                        i.jsx)("tbody", {
                            children: s && s.characterStats.length > 0 ? s.characterStats.slice(0, 10).map((function(e, t) {
                                var a = o(e.key);
                                return (0,
                                i.jsxs)("tr", {
                                    children: [(0,
                                    i.jsx)("td", {
                                        className: "character",
                                        children: (0,
                                        i.jsxs)("div", {
                                            children: [(0,
                                            i.jsx)(F(), {
                                                href: "/characters/".concat(null === a || void 0 === a ? void 0 : a.key),
                                                children: (0,
                                                i.jsx)("a", {
                                                    className: "image-wrapper",
                                                    target: "_blank",
                                                    children: (0,
                                                    i.jsx)("img", {
                                                        src: null === a || void 0 === a ? void 0 : a.imageUrl,
                                                        alt: null === a || void 0 === a ? void 0 : a.name
                                                    })
                                                })
                                            }), (0,
                                            i.jsxs)("div", {
                                                className: "info",
                                                children: [(0,
                                                i.jsx)("div", {
                                                    className: "character-name",
                                                    children: null === a || void 0 === a ? void 0 : a.name
                                                }), (0,
                                                i.jsxs)("div", {
                                                    className: "plays",
                                                    children: [e.play, " ", n("statCategory.game")]
                                                })]
                                            })]
                                        })
                                    }), (0,
                                    i.jsx)("td", {
                                        className: "most-kill",
                                        children: (null === e || void 0 === e ? void 0 : e.maxPlayerKill) > 0 ? null === e || void 0 === e ? void 0 : e.maxPlayerKill : "-"
                                    }), (0,
                                    i.jsx)("td", {
                                        className: "avg-rank",
                                        children: (0,
                                        y.ZD)(null === e || void 0 === e ? void 0 : e.avgPlace)
                                    }), (0,
                                    i.jsx)("td", {
                                        className: "avg-top3",
                                        children: (0,
                                        y.c2)(null === e || void 0 === e ? void 0 : e.top3, null === e || void 0 === e ? void 0 : e.play)
                                    })]
                                }, t)
                            }
                            )) : (0,
                            i.jsx)("tr", {
                                children: (0,
                                i.jsx)("td", {
                                    className: "no-record",
                                    colSpan: 4,
                                    children: (0,
                                    i.jsx)(Un.Z, {
                                        type: "noRecord"
                                    })
                                })
                            })
                        })]
                    })]
                }), (0,
                i.jsx)(F(), {
                    href: {
                        pathname: "/players/".concat(r, "/character/"),
                        query: c
                    },
                    children: (0,
                    i.jsxs)("a", {
                        children: [(0,
                        i.jsx)("span", {
                            children: n("moreCharacterStats")
                        }), (0,
                        i.jsx)(Be, {})]
                    })
                })]
            })
        }
          , Te = s.Z.div(Le())
          , Ke = s.Z.section(De())
          , Ee = t(18687)
          , _e = t(79642);
        function Oe() {
            var n = (0,
            a.Z)(["\n  border: 1px solid #e6e6e6;\n  background: #ffffff;\n\n  > header {\n    padding: 14px 0px 14px;\n    border-bottom: 1px solid #e6e6e6;\n\n    > h2 {\n      display: flex;\n      align-items: center;\n      justify-content: center;\n      gap: 2px;\n\n      font-size: 14px;\n      font-weight: 600;\n      line-height: 14px;\n      color: #646464;\n      text-align: center;\n\n      > span {\n        font-size: 12px;\n        font-weight: 400;\n        line-height: 12px;\n        color: #808080;\n      }\n    }\n  }\n\n  > .recent-match-wrapper {\n    height: 169px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    padding: 0px 17px;\n  }\n\n  > .total-stat-link {\n    display: block;\n    background: #464188;\n    width: 100%;\n    color: #ffffff;\n    text-align: center;\n    padding: 12px;\n    font-size: 14px;\n    line-height: 14px;\n\n    &.recent {\n      background: #88414f;\n    }\n  }\n"]);
            return Oe = function() {
                return n
            }
            ,
            n
        }
        function Pe() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  justify-content: center;\n  align-items: center;\n  column-gap: 12px;\n  padding: 16px 19px 20px 19px;\n  height: 106px;\n\n  > img {\n    width: 64px;\n    height: 64px;\n  }\n\n  > div {\n    display: flex;\n    flex-direction: column;\n    row-gap: 6px;\n\n    &.no-record {\n      font-size: 12px;\n      line-height: 12px;\n      color: #808080;\n    }\n\n    > div {\n      display: flex;\n      font-size: 12px;\n      font-weight: 600;\n      line-height: 12px;\n      gap: 4px;\n\n      > b {\n        font-weight: 600;\n        color: #646464;\n      }\n\n      > span {\n        color: #808080;\n      }\n    }\n  }\n"]);
            return Pe = function() {
                return n
            }
            ,
            n
        }
        function Ge() {
            var n = (0,
            a.Z)(["\n  padding: 15px 19px;\n  border-top: 1px solid #e6e6e6;\n  border-bottom: ", ";\n  display: grid;\n  gap: 12px;\n  grid-template-columns: 1fr 1fr 1fr;\n\n  ", " {\n    grid-template-columns: 1fr 1fr 1fr 1fr 1fr;\n  }\n\n  ", " {\n    grid-template-columns: 1fr 1fr 1fr;\n  }\n"]);
            return Ge = function() {
                return n
            }
            ,
            n
        }
        var Fe = function(n) {
            var e, t = n.teamMode, a = void 0 === t ? "SQUAD" : t, o = n.hideBottom, s = (0,
            l.$G)("player").t, c = (0,
            g.Z)(), d = c.name, p = c.isNormalSeason, x = (c.isLegacySeason,
            (0,
            v.f)(d).data), h = (0,
            m.dN)().data, f = b.AN.SQUAD_RUMBLE, u = b.Vo[a], j = (0,
            r.useMemo)((function() {
                var n;
                if (x) {
                    var e = null === (n = x.playerSeasonOverviews) || void 0 === n ? void 0 : n.find((function(n) {
                        return n.matchingModeId === f && n.teamModeId === u
                    }
                    ));
                    return e
                }
            }
            ), [x, f, u]), y = (0,
            r.useMemo)((function() {
                return j ? j.recentMatches.map((function(n) {
                    return {
                        rank: n.gameRank,
                        isEscape: 3 === n.escapeState
                    }
                }
                )) : []
            }
            ), [j]), C = w(j), Z = C.formatStats, M = C.percents, R = null === (e = null === h || void 0 === h ? void 0 : h.seasons.find((function(n) {
                return n.key === (null === x || void 0 === x ? void 0 : x.meta.season)
            }
            ))) || void 0 === e ? void 0 : e.name;
            return (0,
            i.jsxs)(Ie, {
                children: [(0,
                i.jsx)("header", {
                    children: (0,
                    i.jsxs)("h2", {
                        children: [s("gameMode.squad_rumble"), (0,
                        i.jsxs)("span", {
                            children: ["(", p ? s("gameMode.total") : R, ")"]
                        })]
                    })
                }), (0,
                i.jsxs)($e, {
                    children: [(0,
                    i.jsx)("img", {
                        src: "".concat(k.DX, "/common/img-gamemode-normal.png"),
                        alt: s("gameMode.squad_rumble")
                    }), j ? (0,
                    i.jsxs)("div", {
                        children: [(0,
                        i.jsxs)("div", {
                            children: [(0,
                            i.jsx)("b", {
                                children: s("statCategory.plays")
                            }), (0,
                            i.jsx)("span", {
                                children: Z.plays
                            })]
                        }), (0,
                        i.jsxs)("div", {
                            children: [(0,
                            i.jsx)("b", {
                                children: s("statCategory.avgRank")
                            }), (0,
                            i.jsx)("span", {
                                children: Z.avgRank
                            })]
                        }), (0,
                        i.jsxs)("div", {
                            children: [(0,
                            i.jsx)("b", {
                                children: s("statCategory.winRate")
                            }), (0,
                            i.jsx)("span", {
                                children: Z.winRate
                            })]
                        })]
                    }) : (0,
                    i.jsx)("div", {
                        className: "no-record",
                        children: s("noRecord")
                    })]
                }), (0,
                i.jsxs)(Ue, {
                    hideBottom: p || o,
                    children: [(0,
                    i.jsx)(N, {
                        percent: M.avgTeamKill,
                        title: s("statCategory.avgTK"),
                        value: Z.avgTeamKill
                    }), (0,
                    i.jsx)(N, {
                        percent: M.winRate,
                        title: s("statCategory.winRate"),
                        value: Z.winRate,
                        color: "green"
                    }), (0,
                    i.jsx)(N, {
                        percent: M.plays,
                        title: s("statCategory.plays"),
                        value: Z.plays
                    }), (0,
                    i.jsx)(N, {
                        percent: M.avgKill,
                        title: s("statCategory.avgKills"),
                        value: Z.avgKill
                    }), (0,
                    i.jsx)(N, {
                        percent: M.top2,
                        title: s("statCategory.top2"),
                        value: Z.top2,
                        color: "blue"
                    }), (0,
                    i.jsx)(N, {
                        percent: M.avgDamageToPlayer,
                        title: s("statCategory.avgDamage"),
                        value: Z.avgDamageToPlayer
                    }), (0,
                    i.jsx)(N, {
                        percent: M.avgAssist,
                        title: s("statCategory.avgAssi"),
                        value: Z.avgAssist
                    }), (0,
                    i.jsx)(N, {
                        percent: M.top3,
                        title: s("statCategory.top3"),
                        value: Z.top3,
                        color: "blue"
                    }), (0,
                    i.jsx)(N, {
                        percent: M.avgRank,
                        title: s("statCategory.avgRank"),
                        value: Z.avgRank
                    })]
                }), !p && !o && (0,
                i.jsx)("div", {
                    className: "recent-match-wrapper",
                    children: (0,
                    i.jsx)(W, {
                        matches: y
                    })
                }), p && (0,
                i.jsx)(F(), {
                    href: "/players/".concat(d, "?gameMode=SQUAD_RUMBLE"),
                    children: (0,
                    i.jsx)("a", {
                        className: "total-stat-link recent",
                        children: s("viewRecentStatistics")
                    })
                })]
            })
        }
          , Ie = s.Z.section(Oe())
          , $e = s.Z.div(Pe())
          , Ue = s.Z.div(Ge(), (function(n) {
            return n.hideBottom ? "none" : "1px solid #e6e6e6"
        }
        ), f.B2.md, f.B2.lg);
        function Qe() {
            var n = (0,
            a.Z)(["\n  width: 100%;\n"]);
            return Qe = function() {
                return n
            }
            ,
            n
        }
        function qe() {
            var n = (0,
            a.Z)(["\n  position: relative;\n  height: 44px;\n  padding-left: 16px;\n  padding-right: 8px;\n  display: flex;\n  justify-content: space-between;\n  align-items: center;\n  border-radius: 4px;\n  overflow: hidden;\n  cursor: pointer;\n\n  &::before {\n    display: block;\n    content: '';\n    position: absolute;\n    box-sizing: border-box;\n    left: 0;\n    top: 0;\n    width: 100%;\n    height: 100%;\n    border: 1px solid #e6e6e6;\n    border-radius: 4px;\n    background: ", ";\n  }\n\n  &::after {\n    display: block;\n    content: '';\n    position: absolute;\n    box-sizing: border-box;\n    left: 0;\n    top: 0;\n    height: 100%;\n    background: ", ";\n    width: 4px;\n  }\n\n  > div {\n    display: flex;\n    align-items: center;\n    gap: 6px;\n    z-index: 1;\n\n    > strong {\n      font-weight: 600;\n      font-size: 14px;\n      line-height: 14px;\n      color: ", ";\n    }\n  }\n\n  &.opened {\n    svg {\n      transform: rotateZ(180deg);\n    }\n  }\n\n  > .tier {\n    z-index: 1;\n  }\n"]);
            return qe = function() {
                return n
            }
            ,
            n
        }
        function Ve() {
            var n = (0,
            a.Z)(["\n  padding: 7px 11px;\n  border: 1px solid #e6e6e6;\n  border-radius: 4px;\n  margin-top: 2px;\n  background: #fafafa;\n\n  > ul {\n    display: flex;\n    flex-direction: column;\n  }\n"]);
            return Ve = function() {
                return n
            }
            ,
            n
        }
        function Xe() {
            var n = (0,
            a.Z)(["\n  height: 36px;\n  align-items: center;\n  display: flex;\n\n  > .character-icon {\n    margin-right: 4px;\n    width: 24px;\n    height: 24px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    border-radius: 12px;\n    overflow: hidden;\n\n    > img {\n      width: 100%;\n      height: 100%;\n      object-fit: cover;\n      object-position: center;\n    }\n  }\n\n  > a {\n    &:hover {\n      text-decoration: underline;\n    }\n  }\n\n  > .name {\n    font-size: 12px;\n    line-height: 12px;\n    color: #666a7a;\n  }\n\n  > .player-tag {\n    font-weight: 600;\n    font-size: 11px;\n    line-height: 12px;\n    color: #848999;\n    height: 16px;\n    padding: 0 6px;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    margin-left: 6px;\n    background: #e9eaed;\n    border-radius: 16px;\n  }\n"]);
            return Xe = function() {
                return n
            }
            ,
            n
        }
        function He(n) {
            var e = n.team
              , t = n.playerName
              , a = (0,
            r.useState)(!1)
              , l = a[0]
              , o = a[1]
              , s = (0,
            m.ST)().data
              , c = {
                N: "#A5A8B4",
                F: "#666A7A",
                E: "#724E38",
                D: "#5E73BA",
                C: "#CA9372",
                B: "#11B288",
                A: "#B04DFF",
                S: "#5393CA",
                SS: "#1BB5CA",
                SSS: "#E09500"
            }
              , p = {
                N: "#D6D6D6",
                F: "#808080",
                E: "#844620",
                D: "#19276C",
                C: "#956C38",
                B: "#08A079",
                A: "#8F47CD",
                S: "#207AC7",
                SS: "#0D9EC6",
                SSS: "#EAAF30"
            }
              , x = function(n, e) {
                var t = ["S", "SS", "SSS"].includes(n)
                  , a = "highlight" === e ? c : p;
                return t ? a[n] : a[n[0]]
            }
              , h = ["NONE", "F", "FF", "FFF", "E", "D", "DD", "DDD", "C", "CC", "CCC", "B", "BB", "BBB", "A", "AA", "AAA", "S", "SS", "SSS"][[0, 10, 13, 16, 20, 30, 33, 36, 40, 43, 46, 50, 53, 56, 60, 63, 66, 70, 80, 90].findIndex((function(n) {
                return n === e.ti
            }
            ))]
              , f = x(h, "highlight")
              , u = x(h, "gradient")
              , g = (0,
            I.orderBy)(e.users, "name");
            return (0,
            i.jsxs)(We, {
                children: [(0,
                i.jsxs)(Ye, {
                    $highlightColor: f,
                    $gradientColor: u,
                    onClick: function() {
                        return o((function(n) {
                            return !n
                        }
                        ))
                    },
                    className: d()({
                        opened: l
                    }),
                    children: [(0,
                    i.jsxs)("div", {
                        children: [(0,
                        i.jsx)("strong", {
                            children: e.tnm
                        }), (0,
                        i.jsx)("svg", {
                            width: "8",
                            height: "8",
                            viewBox: "0 0 8 8",
                            fill: "none",
                            xmlns: "http://www.w3.org/2000/svg",
                            children: (0,
                            i.jsx)("path", {
                                d: "M7.45778 1.33337C7.94214 1.33337 8.18432 2.02765 7.8345 2.43791L4.39018 6.47736C4.17491 6.72982 3.82509 6.72982 3.60982 6.47736L0.165495 2.43791C-0.184319 2.02765 0.0578599 1.33337 0.542218 1.33337H7.45778Z",
                                fill: f
                            })
                        })]
                    }), (0,
                    i.jsx)("img", {
                        className: "tier",
                        src: "".concat(k.DX, "/union/tier/img_SquadRumble_Rank_").concat(h, ".png"),
                        width: 36,
                        height: 36,
                        alt: h
                    })]
                }), l && (0,
                i.jsx)(Je, {
                    children: (0,
                    i.jsx)("ul", {
                        children: g.map((function(n) {
                            var e = n.name === t
                              , a = null === s || void 0 === s ? void 0 : s.tiers.find((function(e) {
                                return n.tierId ? e.id === n.tierId : 0 === e.id
                            }
                            ));
                            return (0,
                            i.jsx)("li", {
                                children: (0,
                                i.jsxs)(nt, {
                                    children: [(0,
                                    i.jsx)("div", {
                                        className: "character-icon",
                                        children: (0,
                                        i.jsx)("img", {
                                            src: null === a || void 0 === a ? void 0 : a.iconUrl,
                                            alt: ""
                                        })
                                    }), e ? (0,
                                    i.jsx)("span", {
                                        className: "name",
                                        children: n.name
                                    }) : (0,
                                    i.jsx)(F(), {
                                        href: "/players/".concat(n.name),
                                        children: (0,
                                        i.jsx)("a", {
                                            className: "name",
                                            children: n.name
                                        })
                                    }), e && (0,
                                    i.jsx)("span", {
                                        className: "player-tag",
                                        children: "ME"
                                    })]
                                })
                            }, n.name)
                        }
                        ))
                    })
                })]
            })
        }
        var We = s.Z.div(Qe())
          , Ye = s.Z.div(qe(), (function(n) {
            var e = n.$gradientColor;
            return "linear-gradient(118deg, ".concat(e, "00 76.17%, ").concat(e, " 100%), #ffffff")
        }
        ), (function(n) {
            return n.$highlightColor
        }
        ), (function(n) {
            return n.$highlightColor
        }
        ))
          , Je = s.Z.div(Ve())
          , nt = s.Z.div(Xe());
        function et() {
            var n = (0,
            a.Z)(["\n  margin-top: 12px;\n"]);
            return et = function() {
                return n
            }
            ,
            n
        }
        function tt() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  gap: 6px;\n  padding-left: 4px;\n  margin-bottom: 8px;\n\n  > svg {\n    margin-top: 4px;\n  }\n\n  > span {\n    font-weight: 600;\n    font-size: 12px;\n    line-height: 15.6px;\n    color: #a5a8b4;\n  }\n"]);
            return tt = function() {
                return n
            }
            ,
            n
        }
        function at() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  flex-direction: column;\n  gap: 4px;\n"]);
            return at = function() {
                return n
            }
            ,
            n
        }
        function it() {
            var n = (0,
            l.$G)("player").t
              , e = (0,
            g.Z)().name
              , t = (0,
            v.o1)(e).data
              , a = (0,
            r.useMemo)((function() {
                var n, e = (null !== (n = null === t || void 0 === t ? void 0 : t.teams) && void 0 !== n ? n : []).map((function(n) {
                    return (0,
                    ve.Z)((0,
                    En.Z)({}, n), {
                        users: n.userNums.map((function(n) {
                            var e, a, i = null !== (e = null === t || void 0 === t ? void 0 : t.players.find((function(e) {
                                return e.userNum === n
                            }
                            ))) && void 0 !== e ? e : {}, r = null !== (a = null === t || void 0 === t ? void 0 : t.playerTiers.find((function(e) {
                                return e.userNum === n
                            }
                            ))) && void 0 !== a ? a : {};
                            return (0,
                            En.Z)({
                                userNum: n
                            }, i, r)
                        }
                        ))
                    })
                }
                ));
                return (0,
                I.orderBy)(e, ["ti", "tnm"], ["desc", "asc"])
            }
            ), [t]);
            return 0 === a.length ? null : (0,
            i.jsxs)(rt, {
                children: [(0,
                i.jsxs)(lt, {
                    children: [(0,
                    i.jsx)("svg", {
                        width: "8",
                        height: "8",
                        viewBox: "0 0 8 8",
                        fill: "none",
                        xmlns: "http://www.w3.org/2000/svg",
                        children: (0,
                        i.jsx)("path", {
                            d: "M4 0L5.08036 2.91964L8 4L5.08036 5.08036L4 8L2.91964 5.08036L0 4L2.91964 2.91964L4 0Z",
                            fill: "#A5A8B4"
                        })
                    }), (0,
                    i.jsx)("span", {
                        children: n("unionTeams")
                    })]
                }), (0,
                i.jsx)(ot, {
                    children: a.map((function(n) {
                        return (0,
                        i.jsx)("li", {
                            children: (0,
                            i.jsx)(He, {
                                team: n,
                                playerName: e
                            })
                        }, "".concat(e, "-").concat(n.tnm))
                    }
                    ))
                })]
            })
        }
        var rt = s.Z.div(et())
          , lt = s.Z.div(tt())
          , ot = s.Z.ul(at())
          , st = (t(82262),
        t(83125));
        function ct() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  flex-direction: column;\n  gap: 8px;\n"]);
            return ct = function() {
                return n
            }
            ,
            n
        }
        function dt() {
            var n = (0,
            a.Z)(["\n  margin: 20px 0px;\n"]);
            return dt = function() {
                return n
            }
            ,
            n
        }
        function pt() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  flex-direction: column;\n  row-gap: 20px;\n  column-gap: 12px;\n\n  ", " {\n    flex-direction: row;\n  }\n\n  > .left {\n    display: flex;\n    flex-direction: column;\n    width: 100%;\n\n    ", " {\n      width: 328px;\n    }\n  }\n\n  > .right {\n    flex: 1;\n    display: flex;\n    flex-direction: column;\n    row-gap: 8px;\n  }\n"]);
            return pt = function() {
                return n
            }
            ,
            n
        }
        function xt() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  flex-direction: column;\n  gap: 8px;\n"]);
            return xt = function() {
                return n
            }
            ,
            n
        }
        function ht() {
            var n = (0,
            a.Z)(["\n  display: flex;\n  flex-direction: column;\n  gap: 8px;\n\n  ", " {\n    display: none;\n  }\n"]);
            return ht = function() {
                return n
            }
            ,
            n
        }
        var ft = !0
          , ut = function(n) {
            var e = n.name
              , t = (0,
            l.$G)("seo").t
              , a = "".concat(e, " - ").concat(t("player.profile.title"))
              , s = (0,
            p.Z)(a).title
              , c = (0,
            st.b)().isMobileApp
              , f = (0,
            g.Z)()
              , j = f.seasonQuery
              , y = f.isNormalSeason
              , w = f.gameModeQuery
              , b = f.characterQuery
              , k = (0,
            u.Z)({}).isLoading
              , C = (0,
            v.lp)(void 0, b).isLoading
              , N = (0,
            m.PM)().isLoading
              , Z = (0,
            v.f)(e).isLoading
              , M = (0,
            v.o1)(e).isLoading
              , R = (0,
            r.useState)(!0)[0]
              , A = "LEGACY" === j
              , S = (0,
            Ee.W7)(j)
              , L = !S
              , D = (0,
            r.useState)(!0)
              , B = D[0]
              , z = D[1]
              , T = (0,
            r.useCallback)((function() {
                var n = null === window || void 0 === window ? void 0 : window.matchMedia("(min-width:768px)");
                n.matches !== B && z(n.matches)
            }
            ), [B]);
            (0,
            r.useEffect)((function() {
                return T(),
                window.addEventListener("resize", T),
                function() {
                    return window.removeEventListener("resize", T)
                }
            }
            ), [T]);
            var K = k || M || C || N || Z || !R;
            return (0,
            i.jsxs)(i.Fragment, {
                children: [(0,
                i.jsx)(o.PB, {
                    title: s
                }), (0,
                i.jsx)(_e.Z, {
                    placementName: "vertical_sticky",
                    alias: "sticky"
                }), (0,
                i.jsxs)(x.Z, {
                    playerName: e,
                    children: [(0,
                    i.jsx)(h.Z, {
                        activeTab: "main",
                        isLoading: K
                    }), (0,
                    i.jsxs)(jt, {
                        className: d()(["mobile-tab-wrapper", {
                            early: S
                        }]),
                        children: [(0,
                        i.jsx)(Kn.Z, {}), (0,
                        i.jsx)(Se.Z, {})]
                    }), (0,
                    i.jsx)(zn, {
                        isLoading: K
                    }), K ? (0,
                    i.jsx)(Re, {}) : (0,
                    i.jsx)(i.Fragment, {
                        children: (0,
                        i.jsxs)(mt, {
                            children: [(0,
                            i.jsx)("div", {
                                className: "left",
                                children: A ? (0,
                                i.jsx)(ze, {}) : (0,
                                i.jsxs)(i.Fragment, {
                                    children: [y ? (0,
                                    i.jsx)(vt, {
                                        children: "COBALT" === w ? (0,
                                        i.jsx)(dn, {}) : "SQUAD_RUMBLE" === w ? (0,
                                        i.jsx)(Fe, {}) : (0,
                                        i.jsx)(tn, {})
                                    }) : !L || "ALL" !== w && "RANK" !== w ? "NORMAL" === w ? (0,
                                    i.jsx)(tn, {
                                        hideBottom: !0
                                    }) : "COBALT" === w ? (0,
                                    i.jsx)(dn, {
                                        hideBottom: !0
                                    }) : "SQUAD_RUMBLE" === w ? (0,
                                    i.jsx)(Fe, {
                                        hideBottom: !0
                                    }) : null : (0,
                                    i.jsx)(E, {}), !1, (0,
                                    i.jsx)(it, {}), (0,
                                    i.jsx)(Yn, {
                                        isEarly: S || A
                                    }), !c && !B && (0,
                                    i.jsx)("div", {
                                        style: {
                                            display: "flex",
                                            justifyContent: "center",
                                            alignItems: "center",
                                            marginTop: 20
                                        },
                                        children: (0,
                                        i.jsx)(_e.Z, {
                                            placementName: "mobile_takeover",
                                            alias: "mobile_takeover"
                                        })
                                    }), (0,
                                    i.jsx)(le, {})]
                                })
                            }), (0,
                            i.jsxs)("div", {
                                className: "right",
                                children: [(0,
                                i.jsxs)(gt, {
                                    isNormalSeason: y,
                                    children: [(0,
                                    i.jsx)(Kn.Z, {}), (0,
                                    i.jsx)(Se.Z, {})]
                                }), (0,
                                i.jsx)(ue, {}), (0,
                                i.jsx)(Ce, {})]
                            })]
                        })
                    })]
                })]
            })
        }
          , gt = s.Z.div(ct())
          , mt = (s.Z.div(dt()),
        s.Z.div(pt(), f.B2.xl, f.B2.xl))
          , vt = s.Z.div(xt())
          , jt = s.Z.div(ht(), f.B2.xl)
    },
    97630: function(n, e, t) {
        "use strict";
        var a = t(85893)
          , i = (t(67294),
        t(94184))
          , r = t.n(i)
          , l = t(1922);
        e.Z = function(n) {
            var e = n.type
              , t = n.classStyle
              , i = n.customText
              , o = (0,
            l.$G)("reminder").t;
            return (0,
            a.jsxs)("div", {
                className: r()(t, "flex-center flex-col gap-y-[8px] text-[12px] font-medium text-[#999]"),
                children: [(0,
                a.jsx)("img", {
                    src: "".concat("//cdn.dak.gg", "/er/images/common/character-null.png"),
                    alt: "",
                    width: 136,
                    height: 120
                }), "noData" === e ? o("noData") : "noRecord" === e ? o("noRecord") : "fetchingFail" === e ? o("fetchingFail") : "collecting" === e ? o("collectingData") : "yetData" === e ? o("yetData") : "custom" === e ? i : void 0]
            })
        }
    },
    47795: function(n, e, t) {
        "use strict";
        var a = t(85893);
        t(67294);
        e.Z = function(n) {
            var e = n.classStyle
              , t = n.size
              , i = n.fill;
            return (0,
            a.jsx)("svg", {
                className: e,
                width: t,
                height: t,
                viewBox: "0 0 16 16",
                fill: "none",
                xmlns: "http://www.w3.org/2000/svg",
                children: (0,
                a.jsx)("path", {
                    d: "M5.79221 9.71567C5.98067 10.025 6.22298 10.3063 6.54606 10.5032L6.81529 10.6719L6.43836 11.5719C6.19606 12.1344 5.65759 12.5 5.06529 12.5H3.04606C2.66913 12.5 2.3999 12.2188 2.3999 11.825C2.3999 11.4594 2.66913 11.15 3.04606 11.15H5.06529C5.14606 11.15 5.22683 11.1219 5.25375 11.0375L5.79221 9.71567ZM9.72298 3.50005C8.99606 3.50005 8.43067 2.90942 8.43067 2.15005C8.43067 1.4188 8.99606 0.800049 9.72298 0.800049C10.423 0.800049 11.0153 1.4188 11.0153 2.15005C11.0153 2.90942 10.423 3.50005 9.72298 3.50005ZM12.9537 7.57817C13.3037 7.57817 13.5999 7.88755 13.5999 8.25317C13.5999 8.6188 13.3037 8.92817 12.9268 8.92817H11.6345C10.9614 8.92817 10.3961 8.47817 10.2076 7.80317L9.83067 6.50942C9.77683 6.39692 9.72298 6.28442 9.64221 6.17192L8.51144 9.12505L9.91144 9.99692C10.3691 10.3063 10.6384 10.8125 10.6384 11.3469C10.6384 11.4875 10.6114 11.6563 10.5845 11.7969L9.69606 14.7219C9.61529 15.0313 9.34606 15.2 9.07683 15.2C8.59221 15.2 8.43067 14.75 8.43067 14.525C8.43067 14.4688 8.43067 14.4125 8.45759 14.3563L9.34606 11.4313C9.34606 11.4032 9.34606 11.375 9.34606 11.3469C9.34606 11.2907 9.31913 11.2063 9.23836 11.15L6.97683 9.7438C6.51913 9.43442 6.2499 8.92817 6.2499 8.3938C6.2499 8.19692 6.30375 8.00005 6.38452 7.80317L7.32683 5.32817L6.92298 5.2438C6.84221 5.2438 6.76144 5.21567 6.68067 5.21567C6.43836 5.21567 6.22298 5.30005 6.03452 5.4688L4.71529 6.50942C4.60759 6.5938 4.47298 6.65005 4.33836 6.65005C3.93452 6.65005 3.69221 6.31255 3.69221 5.97505C3.69221 5.77817 3.77298 5.5813 3.93452 5.44067L5.22683 4.40005C5.65759 4.06255 6.16913 3.86567 6.68067 3.86567C6.84221 3.86567 7.03067 3.8938 7.21913 3.92192L9.31913 4.42817C10.1537 4.62505 10.7999 5.27192 11.0691 6.11567L11.4191 7.40942C11.4461 7.52192 11.5537 7.57817 11.6345 7.57817H12.9537Z",
                    fill: i
                })
            })
        }
    },
    63768: function(n, e, t) {
        "use strict";
        t.d(e, {
            a: function() {
                return a
            }
        });
        var a = [{
            key: "seoul",
            name: "Asia"
        }, {
            key: "asia2",
            name: "Asia2"
        }, {
            key: "asia3",
            name: "Asia3"
        }, {
            key: "ohio",
            name: "NA"
        }, {
            key: "frankfurt",
            name: "EU"
        }, {
            key: "saopaulo",
            name: "SA"
        }, {
            key: "global",
            name: "Global"
        }]
    }
}, function(n) {
    n.O(0, [2757, 939, 4968, 6089, 5389, 4599, 9714, 5695, 3591, 8457, 6245, 9774, 2888, 179], (function() {
        return e = 83726,
        n(n.s = e);
        var e
    }
    ));
    var e = n.O();
    _N_E = e
}
]);
